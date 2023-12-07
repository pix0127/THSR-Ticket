from requests.models import Response

from thsr_ticket.controller.confirm_train_flow import ConfirmTrainFlow
from thsr_ticket.controller.confirm_ticket_flow import ConfirmTicketFlow
from thsr_ticket.controller.first_page_flow import FirstPageFlow
from thsr_ticket.view_model.error_feedback import ErrorFeedback
from thsr_ticket.view_model.booking_result import BookingResult
from thsr_ticket.view.web.show_error_msg import ShowErrorMsg
from thsr_ticket.view.web.show_booking_result import ShowBookingResult
from thsr_ticket.view.common import history_info
from thsr_ticket.model.db import (
    ParamDB,
    Record,
    RecordFirstPage,
    RecordTrainPage,
    RecordTicketPage,
)
from thsr_ticket.remote.http_request import HTTPRequest

max_retries = 5


class BookingFlow:
    def __init__(self) -> None:
        self.client = HTTPRequest()
        self.db = ParamDB()
        self.record = Record()
        self.error_feedback = ErrorFeedback()
        self.show_error_msg = ShowErrorMsg()

    def __run(self) -> Response:
        # First page. Booking options
        book_resp, book_model = FirstPageFlow(
            client=self.client, record=self.record
        ).run()
        if self.show_error(book_resp.content):
            return book_resp

        # Second page. Train confirmation
        train_resp, train_model = ConfirmTrainFlow(
            self.client, book_resp, self.record
        ).run()
        if self.show_error(train_resp.content):
            return train_resp

        # Final page. Ticket confirmation
        ticket_resp, ticket_model = ConfirmTicketFlow(
            self.client, train_resp, self.record
        ).run()
        if self.show_error(ticket_resp.content):
            return ticket_resp

        # Result page.
        result_model = BookingResult().parse(ticket_resp.content)
        book = ShowBookingResult()
        book.show(result_model)
        print("\n請使用官方提供的管道完成後續付款以及取票!!")
        return ticket_resp

    def auto_run(self):
        hist = self.db.get_history()
        remove_list = []
        for i in hist:
            self.record = i
            count = 0
            while count < max_retries:
                if self.is_error(self.__run().content):
                    count += 1
                    self.client = HTTPRequest()
                else:
                    break
            if count == max_retries:
                print("第{}筆訂購失敗".format(hist.index(i) + 1))
            else:
                print("第{}筆訂購成功".format(hist.index(i) + 1))
                remove_list.append(hist.index(i) + 1)
        for i in remove_list:
            self.db.remove(i)

    def add_new_reserve(self):
        book_resp, first_data = FirstPageFlow(self.client).check_info()
        if self.show_error(book_resp.content):
            return book_resp
        train_data = ConfirmTrainFlow(self.client, book_resp).check_info()
        number = int("".join(filter(str.isdigit, first_data.adult_num[0])))
        tickit_data = self.get_ticket_data(number)
        self.db.save(first_data, train_data, tickit_data)

    def get_ticket_data(self, adult_num: int) -> RecordTicketPage:
        rst = RecordTicketPage()
        personal_id = []
        for i in range(adult_num):
            personal_id.append(input("請輸入第%i位身分證字號：" % (i + 1)))
        phone = input("請輸入手機號碼：")
        email = input("請輸入email：")
        rst.personal_id = personal_id
        rst.phone = phone
        rst.email = email
        return rst

    def show_history(self) -> None:
        hist = self.db.get_history()
        if not hist:
            return
        h_idx = history_info(hist)
        if h_idx is not None:
            self.record = hist[h_idx]

    def show_error(self, html: bytes) -> bool:
        errors = self.error_feedback.parse(html)
        if len(errors) == 0:
            return False

        self.show_error_msg.show(errors)
        return True

    def is_error(self, html: bytes) -> bool:
        errors = self.error_feedback.parse(html)
        if len(errors) == 0:
            return False
        return True
