import json
from typing import Tuple

from bs4 import BeautifulSoup
from requests.models import Response
from thsr_ticket.configs.web.param_schema import ConfirmTicketModel

from thsr_ticket.model.db import Record
from thsr_ticket.remote.http_request import HTTPRequest


class ConfirmTicketFlow:
    id = []
    def __init__(
        self, client: HTTPRequest, train_resp: Response, record: Record = None
    ):
        self.client = client
        self.train_resp = train_resp
        self.record = record

    def run(self) -> Tuple[Response]:
        page = BeautifulSoup(self.train_resp.content, features="html.parser")
        ticket_model = ConfirmTicketModel(
            personal_id=self.set_personal_id(),
            phone_num=self.set_phone_num(),
            member_radio=_parse_member_radio(page),
            member_id=self.set_member_id(),
            early_member0_id=self.set_early_member_id(0, page),
            early_member1_id=self.set_early_member_id(1, page),
            early_member2_id=self.set_early_member_id(2, page),
        )

        json_params = ticket_model.json(by_alias=True)
        dict_params = json.loads(json_params)
        resp = self.client.submit_ticket(dict_params)
        return resp, ticket_model

    def set_personal_id(self) -> str:
        if self.record and (personal_id := self.record.personal_id[0]):
            self.id = personal_id
            return personal_id
        self.id = input(f"輸入身分證字號：\n")
        return self.id

    def set_phone_num(self) -> str:
        if self.record and (phone_num := self.record.phone):
            return phone_num

        if phone_num := input('輸入手機號碼（預設：""）：\n'):
            return phone_num
        return ""
    
    def set_member_id(self) -> str:
        if len(self.id) > 0 and (personal_id := self.record.personal_id[0]):
            return personal_id
        return None

    def set_early_member_id(self, num: int, page: BeautifulSoup) -> str:
        if len(self.id) < num:
            return None
        if page.find_all(attrs={"class":"uk-input passengerDataIdNumber"}).__len__() > num:
            return self.id[num]
        return None


def _parse_member_radio(page: BeautifulSoup) -> str:
    candidates = page.find_all(
        "input",
        attrs={
            "name": "TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup"
        },
    )
    tag = next((cand for cand in candidates if cand.get('id')=="memberSystemRadio1"))
    return tag.attrs["value"]
    
