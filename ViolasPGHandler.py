import logging

from ViolasModules import ViolasAddressInfo, ViolasTransaction

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

class ViolasPGHandler():
    def __init__(self, dbUrl):
        self.engine = create_engine(dbUrl)
        self.session = sessionmaker(bind = self.engine)

        return

    def commit(self, session):
        for i in range(5):
            try:
                session.commit()
            except OperationalError:
                logging.debug(f"ERROR: Commit failed! Retry after {i} second.")
                sleep(i)

                continue

            return True

        return False

    def InsertTransaction(self, data):
        tran = ViolasTransaction(
            sender = data.get("sender"),
            sequence_number = data.get("sequence_number"),
            max_gas_amount = data.get("max_gas_amount"),
            gas_unit_price = data.get("gas_unit_price"),
            expiration_time = data.get("expiration_time"),
            transaction_type = data.get("transaction_type"),
            receiver = data.get("receiver"),
            amount = data.get("amount"),
            module = data.get("module"),
            data = data.get("data"),
            public_key = data.get("public_key"),
            signature = data.get("signature"),
            transaction_hash = data.get("transaction_hash"),
            state_root_hash = data.get("state_root_hash"),
            event_root_hash = data.get("event_root_hash"),
            gas_used = data.get("gas_used"),
            status = data.get("status")
        )
        s = self.session()

        s.add(tran)
        self.commit(s)

        s.close()

        return

    def InsertTransactions(self, data):
        s = self.session()

        transactions = []
        for i in data:
            tran = ViolasTransaction(
                sender = i.get("sender"),
                sequence_number = i.get("sequence_number"),
                max_gas_amount = i.get("max_gas_amount"),
                gas_unit_price = i.get("gas_unit_price"),
                expiration_time = i.get("expiration_time"),
                transaction_type = i.get("transaction_type"),
                receiver = i.get("receiver"),
                amount = i.get("amount"),
                module = i.get("module"),
                data = i.get("data"),
                public_key = i.get("public_key"),
                signature = i.get("signature"),
                transaction_hash = i.get("transaction_hash"),
                state_root_hash = i.get("state_root_hash"),
                event_root_hash = i.get("event_root_hash"),
                gas_used = i.get("gas_used"),
                status = i.get("status")
            )

            transactions.append(tran)

        s.add_all(transactions)
        self.commit(s)
        s.close()
        return

    def HandleSenderAddressInfo(self, data):
        s = self.session()

        if data["transaction_type"] == "mint" or data["transaction_type"] == "violas_mint":
            sent_minted_tx_count = 1
        else:
            sent_minted_tx_count = 0

        if data["status"] != 4001:
            sent_failed_tx_count = 1
            sent_amount = 0
        else:
            sent_failed_tx_count = 0
            sent_amount = data["amount"]

        for i in range(5):
            try:
                result = s.query(ViolasAddressInfo).filter(ViolasAddressInfo.address == data["sender"]).first()
            except OperationalError:
                logging.debug(f"ERROR: Query failed! Retry after {i} second!")
                sleep(i)
                continue

            break

        if result is None:
            info = ViolasAddressInfo(
                address = data["sender"],
                type = data["address_type"],
                first_seen = data["version"],
                sent_amount = sent_amount,
                sent_tx_count = 1,
                sent_minted_tx_count = sent_minted_tx_count,
                sent_failed_tx_count = sent_failed_tx_count,
                received_amount = 0,
                received_tx_count = 0,
                received_minted_tx_count = 0,
                received_failed_tx_count = 0
            )

            s.add(info)
        else:
            result.sent_amount += sent_amount
            result.sent_tx_count += 1
            result.sent_minted_tx_count += sent_minted_tx_count
            result.sent_failed_tx_count += sent_failed_tx_count

        self.commit(s)
        s.close()
        return

    def HandleReceiverAddressInfo(self, data):
        s = self.session()

        if data["transaction_type"] == "mint" or data["transaction_type"] == "violas_mint":
            received_minted_tx_count = 1
        else:
            received_minted_tx_count = 0

        if data["status"] != 4001:
            received_failed_tx_count = 1
            received_amount = 0
        else:
            received_failed_tx_count = 0
            received_amount = data["amount"]

        for i in range(5):
            try:
                result = s.query(ViolasAddressInfo).filter(ViolasAddressInfo.address == data["receiver"]).first()
            except OperationalError:
                logging.debug(f"ERROR: Query failed! Retry after {i} second!")
                sleep(i)
                continue

            break

        if result is None:
            info = ViolasAddressInfo(
                address = data["receiver"],
                type = data["address_type"],
                first_seen = data["version"],
                received_amount = received_amount,
                received_tx_count = 1,
                received_minted_tx_count = received_minted_tx_count,
                received_failed_tx_count = received_failed_tx_count,
                sent_amount = 0,
                sent_tx_count = 0,
                sent_minted_tx_count = 0,
                sent_failed_tx_count = 0
            )

            s.add(info)
        else:
            result.received_amount += received_amount
            result.received_tx_count += 1
            result.received_minted_tx_count += received_minted_tx_count
            result.received_failed_tx_count += received_failed_tx_count

        self.commit(s)
        s.close()
        return

    def GetTransactionCount(self):
        s = self.session()

        for i in range(5):
            try:
                result = s.query(ViolasTransaction).count()
            except OperationalError:
                logging.debug(f"ERROR: Query failed! Retry after {i} second!")
                sleep(i)
                continue

            break

        s.close()

        return result
