import os
from typing import Mapping, List, Iterable, Any, NamedTuple, Tuple

from tinydb import TinyDB, Query
from tinydb.database import Document

from thsr_ticket import MODULE_PATH
from thsr_ticket.configs.web.param_schema import (
    BookingModel,
    ConfirmTicketModel,
    ConfirmTrainModel,
)


class Record(NamedTuple):
    personal_id: List[str] = None
    phone: str = None
    email: str = None
    start_station: int = None
    dest_station: int = None
    outbound_date: str = None
    outbound_time: str = None
    adult_num: str = None
    selection_time: List[str] = None


class RecordFirstPage:
    start_station: int = None
    dest_station: int = None
    outbound_date: str = None
    outbound_time: str = None
    adult_num: str = None


class RecordTrainPage:
    selection_time: List[str] = None


class RecordTicketPage:
    personal_id: List[str] = None
    phone: str = None
    email: str = None


class ParamDB:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(MODULE_PATH, ".db", "history.json")
        self.db_path = db_path
        db_dir = db_path[: db_path.rfind("/")]
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def save(
        self,
        book_model: BookingModel,
        ticket: ConfirmTicketModel,
        train: ConfirmTrainModel,
    ) -> None:
        data = Record(
            ticket.personal_id,
            ticket.phone_num,
            ticket.email,
            book_model.start_station,
            book_model.dest_station,
            book_model.outbound_date,
            book_model.outbound_time,
            book_model.adult_ticket_num,
            train.selected_train,
        )._asdict()  # type: ignore
        with TinyDB(self.db_path, sort_keys=True, indent=4) as db:
            hist = db.search(Query().personal_id == ticket.personal_id)
            if self._compare_hist(data, hist) is None:
                db.insert(data)

    def save(
        self, first: RecordFirstPage, train: RecordTrainPage, ticket: RecordTicketPage
    ) -> None:
        data = Record(
            ticket.personal_id,
            ticket.phone,
            ticket.email,
            first.start_station,
            first.dest_station,
            first.outbound_date,
            first.outbound_time,
            first.adult_num,
            train.selection_time,
        )._asdict()
        with TinyDB(self.db_path, sort_keys=True, indent=4) as db:
            db.insert(data)
    
    def save(self, data: Record) -> None:
        with TinyDB(self.db_path, sort_keys=True, indent=4) as db:
            db.insert(data._asdict())

    def get_history(self) -> List[Tuple[int, Record]]:
        with TinyDB(self.db_path) as db:
            dicts = db.all()
        return [[d.doc_id, Record(**d)] for d in dicts]  # type: ignore

    def _compare_hist(self, data: Mapping[str, Any], hist: Iterable[Document]) -> int:
        for idx, h in enumerate(hist):
            comp = [h[k] for k in data.keys() if h[k] == data[k]]
            if len(comp) == len(data):
                return idx
        return None

    def remove(self, idx: int) -> None:
        with TinyDB(self.db_path) as db:
            db.remove(doc_ids=[idx])
