import json
from typing import List, Tuple

from requests.models import Response

from thsr_ticket.model.db import Record
from thsr_ticket.remote.http_request import HTTPRequest
from thsr_ticket.view_model.avail_trains import AvailTrains
from thsr_ticket.configs.web.param_schema import Train, ConfirmTrainModel


class ConfirmTrainFlow:
    def __init__(self, client: HTTPRequest, book_resp: Response, record: Record = None):
        self.client = client
        self.book_resp = book_resp
        self.record = record

    def run(self) -> Tuple[Response, ConfirmTrainModel]:
        trains = AvailTrains().parse(self.book_resp.content)
        if not trains:
            raise ValueError("No available trains!")
        confirm_model = ConfirmTrainModel(
            #selected_train=self.select_available_trains(trains),
            selected_train=self.select_available_trains_with_trainid(trains, self.record.selection_time),
        )
        json_params = confirm_model.json(by_alias=True)
        dict_params = json.loads(json_params)
        resp = self.client.submit_train(dict_params)
        return resp, confirm_model

    def select_available_trains(
        self, trains: List[Train], default_value: int = 1
    ) -> Train:
        if self.record and self.record.selected_train != None:
            return self.record.selected_train
        for idx, train in enumerate(trains, 1):
            print(
                f"{idx}. {train.id:>4} {train.depart:>3}~{train.arrive} {train.travel_time:>3} "
                f"{train.discount_str}"
            )
        selection = int(input(f"輸入選擇（預設：{default_value}）：") or default_value)
        return trains[selection - 1].form_value

    def select_available_trains_with_trainid(
        self, trains: List[Train], trains_leavetime: List[str]
    ) -> Train:
        for id in trains_leavetime:
            rst = self.get_form_value_by_id(trains, id)
            if rst != None:
                return rst
        return None

    def get_form_value_by_id(self, trains: List[Train], leavetime: str) -> Train:
        train = next((train for train in trains if train.depart == leavetime), None)
        return train.form_value if train else None
