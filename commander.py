import telegram
from alert import Alerts
from conf import Configuration
from telegram.ext import CommandHandler
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup


class Commander(Configuration):
    def __init__(self, handle):
        super().__init__()
        self.handle = handle
        self.alerts = Alerts()
        self.U = self.commander["paisheeBot"]

        self.commies = [
            CommandHandler("scrip", self._scrip),
            CommandHandler("analysis", self._analysis),
            CommandHandler("status", self._status),
        ]
        self.U.dispatcher.add_handler(self.commies[0])
        self.U.start_polling(
            clean=True,
            bootstrap_retries=-1,
            timeout=30,
            read_latency=60,
        )

        # self.replyMarkup = [
        #     CommandHandler("analysis", self._analysis),
        #     CommandHandler("scrip", self._scrip),
        #     CommandHandler("status", self._status),
        # ]

    def _analysis(self, update, context):
        pass

    def _status(self, update, context):
        pass

    def _scrip(self, update, context):
        scrip = context.args[0].upper()
        print(self.handle.stratdf.keys())
        Text = self.handle.stratdf[scrip].tail().to_html()
        keyboard = [['/daily', '/profit', '/balance'],
                    ['/status', '/status table', '/performance'],
                    ['/count', '/start', '/stop', '/help']]
        reply_markup = ReplyKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=Text,
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    def _send_msg(self, msg: str, parse_mode = telegram.ParseMode.HTML, disable_notification: bool = False) -> None:
        keyboard = [['/daily', '/profit', '/balance'],
                    ['/status', '/status table', '/performance'],
                    ['/count', '/start', '/stop', '/help']]

        reply_markup = ReplyKeyboardMarkup(keyboard)

        self._updater.bot.send_message(
            self._config['telegram']['chat_id'],
            text=msg,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_notification=disable_notification,
        )