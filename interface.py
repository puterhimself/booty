from os import name
from loguru import logger
from typing import Any

import telegram

from data import databox, 
from data import datahelper as dh 
from processor import processor
from telegram.ext import CommandHandler, callbackcontext
from telegram.error import NetworkError, TelegramError


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    buttons = [f'/{comm}' for comm in buttons]

    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


class interface:

    def __init__(self): 

        self.theBox: databox = databox(lazyload=False)
        self.pro: processor = processor()
        logger.info('-> InterFacing')
        
        self.bot = self.theBox.bot
        self._dis = self.theBox.updater.dispatcher
        self._upd = self.theBox.updater
        self.shots = [
            'init',
            'squeeze',
            'update',
            'bangs',
            'prize',
        ]
        logger.info('-- init commands')

        for shot in self.shots:
            self._dis.add_handler(CommandHandler(
                shot, getattr(self, f'_{shot}')
            ))
            logger.debug(f'-- (͠≖ ͜ʖ͠≖)👌 {shot} ')
            
        self._upd.start_polling(clean=True, timeout=30,)


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