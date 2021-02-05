import re
from satish import satish
from backtesting.backtesting import Backtest
from loguru import logger

import telegram
from telegram.update import Update
from telegram import ChatAction, InlineKeyboardButton
from telegram.error import NetworkError, TelegramError
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.ext import (
    Filters,
    CommandHandler,
    MessageHandler,
    callbackcontext,
    CallbackQueryHandler
    )

from data import databox
from data import datahelper as dh
from satish import simps
from processor import processor
from functools import wraps

def typings(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update,
    context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):

    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu



class statistician:
    
    @logger.catch
    def __init__(self) -> None: 
        self.theBox: databox = databox()
        self.pro: processor = processor()
        self.satish: satish = satish()
        
        logger.info('->Statistician Bot')
        self.bot = self.theBox.updater_.bot
        self._dis = self.theBox.updater_.dispatcher
        self._upd = self.theBox.updater_
        self.options = [
            'init',
            'squeeze',
            'scrips',
            'strats',
            'config',
            'run',
            'stop',
        ]
        buttons = [f'/{comm}' for comm in self.options]
        buttons = build_menu(buttons, 2)
        self.keyboard = telegram.ReplyKeyboardMarkup(buttons)
        logger.debug(f'-- Loading Commands :{" | ".join(self.options)}')

        self.config = dict(
            strategy=simps,
            cash=1000000, 
            commission=0.004, 
            trade_on_close=True,
            margin=0.008,
            exclusive_orders=False)
        logger.bind(meta=self.config).debug('default config')

        logger.debug('adding command handlers to Updater')
        for shot in self.options:
            self._dis.add_handler(CommandHandler(
                shot, getattr(self, f'_{shot}')
            ))
            logger.debug(f'-- (͠≖ ͜ʖ͠≖)👌 {shot} ')
        
        logger.debug('adding other handlers to Updater')
        meta = self.theBox.desc
        
        ptrn = meta['strats']
        ptrn = f'^({ptrn})'
        self._dis.add_handler(CallbackQueryHandler(self._stratsButton, pattern=ptrn))
        logger.bind(meta={'commands': ptrn}).debug(f'-- (͠≖ ͜ʖ͠≖)👌 callback _strat Button ')
        
        ptrn = [f'~{i}|' for i in meta['_strats']]
        ptrn = f'^({ptrn})'
        self._dis.add_handler(CallbackQueryHandler(self._runButton, pattern=ptrn))
        logger.bind(meta={'commands': ptrn}).debug(f'-- (͠≖ ͜ʖ͠≖)👌 callback _run Button ')

        ptrn = meta['btconf']
        ptrn = f'^({ptrn})'
        self._dis.add_handler(CallbackQueryHandler(self._configButton, pattern=ptrn))
        logger.bind(meta={'commands': ptrn}).debug(f'-- (͠≖ ͜ʖ͠≖)👌 callback _conf Button ')
        
        self._dis.add_handler(
            MessageHandler(
                Filters.regex(
                    re.compile(r'^config', re.IGNORECASE)
                    ),
                 self._setconfig
                 )
        )
        logger.bind(meta={'commands': 'config'}).debug(f'-- (͠≖ ͜ʖ͠≖)👌 set config handler')

            
        self._upd.start_polling(clean=True, timeout=30,)
        logger.debug('starting pooling for updater')
        self.flock('You Should probably start working now ( ͡❛ ͜ʖ ͡❛)✊')
    
    
    def _init(self, update: Update, context: callbackcontext):
        meta = self.theBox.desc
        meta['strat'] = '-->'.join(self.theBox.strategiesList)

        msg = (
            '(っ＾▿＾)۶🍸🌟🍺٩(˘◡˘ ) '
            '\n\n{scrips} are loaded, To add more use load function(?)'
            '\n\nFollowing strats are loaded\n'
            '{strat}'
            ).format(**meta)

        self.flock(msg)

        
    def _squeeze(self, update: Update, context: callbackcontext):
        self.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        meta = self.theBox.desc
        self.theBox.squeeze()
        
        msg = '(っ＾▿＾)💨 \n\n {scrips}'.format(**meta)
        self.flock(msg)


    def _scrips(self, update: Update, context: callbackcontext):  
        meta = self.theBox.desc
        msg = 'List of Loaded Coins:\n'
        msg += '\n'.join([f'--> {sc}' for sc in meta['_scrips']])
        self.flock(msg)


    def _strats(self, update: Update, context: callbackcontext):  
        # meta = self.theBox.desc
        self.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        strat = self.theBox.strategiesList
        markup = build_menu([InlineKeyboardButton(st, callback_data=st) for st in strat], 1)
        markup = InlineKeyboardMarkup(markup)
        logger.bind(meta={'strat': strat, 'markup': markup}).debug(f'_strats')

        msg = 'List of Available Strats:\n (⊙.⊙(◉̃_᷅◉)⊙.⊙)'
        self.send(msg, update.effective_chat.id, markup)
           
    def _stratsButton(self, update: Update, context: callbackcontext) -> None:
        self.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        q = update.callback_query; q.answer()
        
        modclass = self.theBox.Strats[q.data]
        meta = {
            'resample': modclass.timeframe,
            '_cols': ['buy', 'sell'],
            }
        msg = (
            f'Loading Strategy {q.data}\n'
            f'Metadata: {str(meta)}'
        )
        q.edit_message_text(text=msg)
        self.theBox.applystrat(modclass, meta)
        
        msg = (
            f'Done loading {q.data}'
            '\nTo run the Strategy press /run'
        )
        self.flock(msg)


    def _config(self, update: Update, context: callbackcontext):  
        self.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        configs = dh.backtestinit.keys()
        markup = build_menu([InlineKeyboardButton(st, callback_data=st) for st in configs], 1)
        markup = InlineKeyboardMarkup(markup)
        logger.bind(meta={'config': self.config, 'markup': markup}).debug(f'_config')

        msg = f'Current Config\n\n{self.config}'
        msg += '\n\n✍(◔◡◔)\n\nList of Available Parameters:'
        
        self.send(msg, update.effective_chat.id, markup)


    def _configButton(self, update: Update, context: callbackcontext) -> None:
        self.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        q = update.callback_query; q.answer()
        configs = dh.backtestinit
        msg = (
            't(>.<t)\n\n'
            f'{q.data}: {configs[q.data]}'
            '\n\n------------------'
            '\nTo set config Try\n'
        )
        q.edit_message_text(text=msg)
        
        msg = (
            f'config {q.data} float(1.0)'
        )
        self.send(msg, update.effective_chat.id)

    def _setconfig(self, update: Update, context: callbackcontext):  
        txt: list = update.message.text.split(' ')
        param , value = txt[1:]
        logger.bind(meta={'params': txt}).debug('Incoming config request')
        if param in self.config.keys() :
            if str(value) in ['1', 't', 'T', 'True']:   value = True
            if str(value) in ['0', 'f', 'F', 'False']:  value = False
            self.config[param] = float(value)
            logger.bind(meta={'params': txt, 'config': self.config}).debug('config changed')
        else:
            logger.bind(meta={'params': txt, 'config': self.config}).debug('key mismatch')


    def run(self, data, config):
        self.backtest = Backtest(data=data, **config)
        results = self.backtest.run()
        return results
        

    @logger.catch
    def _run(self, update: Update, context: callbackcontext):  
        self.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        configs = self.theBox.desc['_mods']
        markup = build_menu([InlineKeyboardButton(st, callback_data=st) for st in configs], 1)
        markup = InlineKeyboardMarkup(markup)
        logger.bind(meta={'config': self.config, 'markup': markup}).debug(f'_run')

        msg = 'ᕙ(`▿´)ᕗ'
        msg += '\nWhat do you want to run??'
        self.send(msg, update.effective_chat.id, markup)
    

    def _runButton(self, update: Update, context: callbackcontext) -> None:
        self.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        q = update.callback_query; q.answer()


    def _stop(self, update: Update, context: callbackcontext):  
        self._upd.stop()


    def flock(self, msg):
        logger.debug('-> Flocking')

        for name, id in self.theBox._Tusers.items():
            self.send(msg, id)
            logger.debug(f'-- flocking to {name}:{id}')


    def send(self, msg: str, id: int, shots=None):
        shots = self.keyboard if shots is None else shots

        try:
            try:
                self.bot.send_chat_action(chat_id=id, action=ChatAction.TYPING)
                self.bot.send_message(
                    text=msg,
                    chat_id=id,
                    reply_markup=shots,
                )
            except NetworkError as network_err:
                # Sometimes the telegram server resets the current connection,
                # if this is the case we send the message again.
                print(
                    'Telegram NetworkError: %s! Trying one more time.',
                    network_err.message
                )
                self.bot.send_message(
                    text=msg,
                    reply_markup=shots,
                    chat_id=id
                )
        except TelegramError as telegram_err:
            print(
                'TelegramError: %s! Giving up on that message.',
                telegram_err.message
            )

if __name__ == "__main__":
    statistician()