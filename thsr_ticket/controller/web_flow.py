from typing import List
from thsr_ticket.remote.http_request import HTTPRequest
from thsr_ticket.model.db import (
    ParamDB,
    Record,
    RecordFirstPage,
    RecordTrainPage,
    RecordTicketPage,
)
from thsr_ticket.view_model.error_feedback import ErrorFeedback
from thsr_ticket.controller.first_page_flow import FirstPageFlow
from thsr_ticket.controller.confirm_train_flow import ConfirmTrainFlow
from thsr_ticket.controller.confirm_ticket_flow import ConfirmTicketFlow
from thsr_ticket.configs.web.param_schema import (
    Train,
    ConfirmTrainModel,
    BookingModel,
    ConfirmTicketModel,
)
from thsr_ticket.view_model.avail_trains import AvailTrains
from enum import Enum


def is_error(html: bytes) -> bool:
    errors = ErrorFeedback().parse(html)
    if len(errors) == 0:
        return False
    return True


class WebFlowState(Enum):
    FIRST_PAGE = 1
    TRAIN_PAGE = 2
    TICKET_PAGE = 3
    RESULT_PAGE = 4


class WebFlow:
    def __init__(self) -> None:
        self.state = WebFlowState.FIRST_PAGE
        self.db = ParamDB()

    def new_flow(self, first_page_data: RecordFirstPage) -> bool:
        self.client = HTTPRequest()
        self.ticket_model = None
        self.train_model = None
        self.book_model = None
        # Is date correct and change ?
        self.only_reserve = False
        book_resp, self.book_model = FirstPageFlow(client=self.client).run(
            first_page_data
        )
        if not is_error(book_resp.content):
            self.state = WebFlowState.TRAIN_PAGE
            self.response = book_resp
            return True
        return False

    def get_train_list(self) -> List[Train]:
        if self.state == WebFlowState.TRAIN_PAGE:
            return AvailTrains().parse(self.response.content)
        return []

    def train_page(self, train_page_data: RecordTrainPage):
        if self.state == WebFlowState.TRAIN_PAGE:
            trains = AvailTrains().parse(self.response.content)
            if not trains:
                self.state = WebFlowState.FIRST_PAGE
                return False
            train_resp, self.train_model = ConfirmTrainFlow(
                self.client, self.response
            ).run(train_page_data)
            if not is_error(train_resp.content):
                self.state = WebFlowState.TICKET_PAGE
                self.response = train_resp
                return True
            self.state = WebFlowState.FIRST_PAGE
            return False
        else:
            return False

    def ticket_page(self, ticket_page_data: RecordTicketPage):
        ret = False
        if self.state == WebFlowState.TICKET_PAGE:
            if self.only_reserve:
                ticket_resp, self.ticket_model = ConfirmTicketFlow(
                    self.client, self.response
                ).run(ticket_page_data)
                self.db.save(self.book_model, self.train_model, self.ticket_model)
                ret = True
            else:
                ticket_resp, self.ticket_model = ConfirmTicketFlow(
                    self.client, self.response
                ).run(ticket_page_data)
                if not is_error(ticket_resp.content):
                    self.response = ticket_resp
                    ret = True
                else:
                    self.db.save(self.book_model, self.train_model, self.ticket_model)
                    ret = True
        self.state = WebFlowState.FIRST_PAGE
        return ret

    def get_result(self):
        return self.response.content
