login_info = [os.environ['USERNAME'], os.environ['PASSWORD']]

from telegram.ext import (Updater, JobQueue, Job, Filters,
                          CallbackQueryHandler, CommandHandler, MessageHandler,
                          ConversationHandler, RegexHandler, Handler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      InlineKeyboardButton, InlineKeyboardMarkup)
import datetime
from datetime import timedelta, time

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


REMEDIO, DOSE, DIA, HORA, REPETICAO, TIPO, PORH, PORD, PORS, PORM, FIM, INI, LISTA1, LISTA2, DELETAR, ALTERAR, ALTREMEDIO, ALTDOSE, ALTDATA, ALTHORA, ALTREPETICAO, ALTPHORA, ALTPDIA, ALTPSEMANA, ALTPMES= range(25)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update, chat_data):
    update.message.reply_text('HappyPill')

    chat_id = update.message.chat_id
    
    keyboard = [['Adicionar remedio'],['Listar remedios']]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    bot.sendMessage(chat_id=chat_id,
                    text='Em que posso ajudar?',
                    reply_markup=reply)
    chat_data['ListaRemedio'] = {}
    chat_data['QtdR'] = 0

def key_select_oquefazer(bot, update, groups, chat_data):
    chat_id = update.message.chat_id
    opcao = groups[0]

    opcoes = {'Adicionar remedio', 'Listar remedios'}
    if opcao in opcoes:
        if opcao == 'Adicionar remedio':
            update.message.reply_text('Qual o remedio?')
            return REMEDIO
        else:
            ListaRemedio = chat_data['ListaRemedio']

            for x in range(1, chat_data['QtdR']+1):
                R = ListaRemedio[x]
                data = R['data']
                hora = R['hora']
                d2 = datetime.datetime(year=data.year, month=data.month, day=data.day, hour=hora.hour, minute=hora.minute)
                now = datetime.datetime.now()
                if (d2 - now).total_seconds() <= 0: #ainda nao aconteceu
                    for y in range(x, chat_data['QtdR']):
                        ListaRemedio[y] = ListaRemedio[y+1]
                    chat_data['QtdR'] -= 1

            if chat_data['QtdR'] == 0:
                bot.sendMessage(chat_id = chat_id,
                                text = 'Voce nao tem remedio na lista')
                keyboard = [['Adicionar remedio'],['Listar remedios']]
                reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                bot.sendMessage(chat_id=chat_id,
                                text='Em que posso ajudar?',
                                reply_markup=reply)
                return INI

            bot.sendMessage(chat_id=chat_id,
                            text='Voce tem %d alarme(s)' % chat_data['QtdR'])
            
            for x in range(1, chat_data['QtdR']+1):
                R = ListaRemedio[x]
                if R['repeticao']['tipo'] == 'nao':
                    bot.sendMessage(chat_id = chat_id,
                                    text='ID: %d, Remedio: %s, Dose: %s, Data: %s, Hora: %s, Sem repeticao' % (x, R['remedio'], R['dose'], R['data'], R['hora']))
                else:
                    bot.sendMessage(chat_id = chat_id,
                                    text='ID: %d, Remedio: %s, Dose: %s, Data inicio: %s, Hora: %s, Repeticao: a cada %d %s' %(x, R['remedio'], R['dose'], R['data'], R['hora'], R['repeticao']['aCada'], R['repeticao']['tipo']))

            chat_data['ListaRemedio'] = ListaRemedio
            
            keyboard=[['Voltar']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=chat_id,
                            text='Digite ID do alarme que deseja alterar ou deletar\nOu pressione o botao Voltar',
                            reply_markup=reply)
            return LISTA1
            
    else:
        keyboard = [['Adicionar remedio'],['Listar remedios']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=chat_id,
                    text='Opcao invalida!\nEm que posso ajudar?',
                    reply_markup=reply)
        return INI

def lista1(bot, update, chat_data):
    chat_id = update.message.chat_id
    resp = update.message.text

    if resp == 'Voltar':
        keyboard = [['Adicionar remedio'],['Listar remedios']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=chat_id,
                    text='Em que posso ajudar?',
                    reply_markup=reply)
        return INI        
    else:
        try:
            resp = int(resp)
            chat_data['IDAtual'] = resp
            if resp > chat_data['QtdR']:
                keyboard=[['Voltar']]
                reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                bot.sendMessage(chat_id=chat_id,
                                text='Opcao invalida!!\nDigite ID do alarme que deseja alterar ou deletar\nOu pressione o botao Voltar',
                                reply_markup=reply)
                return LISTA1

            else:
                R = chat_data['ListaRemedio'][resp]
                if R['repeticao']['tipo'] == 'nao':
                    bot.sendMessage(chat_id = chat_id,
                                    text='ID: %d, Remedio: %s, Dose: %s, Hora: %s, Sem repeticao' % (resp, R['remedio'], R['dose'], R['hora']))
                else:
                    bot.sendMessage(chat_id = chat_id,
                                    text='ID: %d, Remedio: %s, Dose: %s, Hora: %s, Repeticao: a cada %d %s' %(resp, R['remedio'], R['dose'], R['hora'], R['repeticao']['aCada'], R['repeticao']['tipo']))
                keyboard = [['Alterar', 'Deletar'], ['Voltar']]
                reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                bot.sendMessage(chat_id = update.message.chat_id,
                                text='Voce quer realizar qual operacao?',
                                reply_markup=reply)
                return LISTA2
        except:
            keyboard=[['Voltar']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=chat_id,
                            text='Opcao invalida!!\nDigite ID do alarme que deseja alterar ou deletar\nOu pressione o botao Voltar',
                            reply_markup=reply)
            return LISTA1

        
def lista2(bot, update, chat_data):
    resp = update.message.text
    opcoes = {'Alterar', 'Deletar', 'Voltar'}
    if resp in opcoes:
        if resp == 'Alterar':
            keyboard = [['Remedio', 'Dose', 'Data'], ['Hora', 'Repeticao', 'Voltar']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Qual dado do alarme voce quer alterar?',
                            reply_markup=reply)
            return ALTERAR
            
        if resp == 'Deletar':
            keyboard = [['Sim', 'Nao']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id = update.message.chat_id,
                            text='Tem certeza que quer deletar o alarme escolhido?',
                            reply_markup=reply)
            return DELETAR
        if resp == 'Voltar':
            keyboard = [['Adicionar remedio'],['Listar remedios']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Em que posso ajudar?',
                            reply_markup=reply)
            return INI
                            
    else:
        keyboard = [['Alterar', 'Deletar'], ['Voltar']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id = update.message.chat_id,
                        text='Opcao invalida!!\nVoce quer realizar qual operacao?',
                        reply_markup=reply)

def altRemedio(bot, update, chat_data):
    resp = update.message.text
    ID = chat_data['IDAtual']
    remedio = chat_data['ListaRemedio'][ID]
    remedio['remedio'] = resp
    chat_data['ListaRemedio'][ID] = remedio

    keyboard = [['Dose', 'Data'], ['Hora', 'Repeticao', 'Voltar']]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='Voce quer alterar mais algum dado?',
                    reply_markup=reply)
    return ALTERAR
    
def altDose(bot, update, chat_data):
    resp = update.message.text
    ID = chat_data['IDAtual']
    remedio = chat_data['ListaRemedio'][ID]
    remedio['dose'] = resp
    chat_data['ListaRemedio'][ID] = remedio

    keyboard = [['Remedio', 'Data'], ['Hora', 'Repeticao', 'Voltar']]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='Voce quer alterar mais algum dado?',
                    reply_markup=reply)
    return ALTERAR

def altData(bot, update, chat_data):
    resp = update.message.text
    validar = False
    if len(resp) <= 2:
        if len(resp) == 1:
            try:
                dia = int(resp[0])
                validar = True
            except:
                validar = False
        elif len(resp) == 2:
            try:
                dia = int(resp[0]) * 10 + int(resp[1])
                validar = True
            except:
                validar = False
        if validar:
            mes = datetime.datetime.now().month
            ano = datetime.datetime.now().year
    elif len(resp) == 5:
        try:
            dia = int(resp[0]) * 10 + int(resp[1])
            mes = int(resp[3]) * 10 + int(resp[4])
            ano = datetime.datetime.now().year
        except:
            validar = False
    else:
        try:
            dia = int(resp[0]) * 10 + int(resp[1])
            mes = int(resp[3]) * 10 + int(resp[4])
            ano = int(resp[6]) * 1000 + int(resp[7]) * 100 + int(resp[8]) * 10 + int(resp[9])
        except:
            validar = False
    try:
        data = datetime.date(ano, mes, dia)
        validar = True
    except:
        validar = False

    if validar == True:
        ID = chat_data['IDAtual']
        remedio = chat_data['ListaRemedio'][ID]
        remedio['data'] = data
        chat_data['ListaRemedio'][ID] = remedio

        keyboard = [['Remedio', 'Dose'], ['Hora', 'Repeticao', 'Voltar']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Voce quer alterar mais algum dado?',
                        reply_markup=reply)
        return ALTERAR
    else:
        bot.sendMessage(chat_id = chat_id,
                            text = 'Data invalida\nQual nova data do alarme?\nFormato: DD/MM/AAAA')                
        return ALTDATA  
    
def altHora(bot, update, chat_data):
    resp = update.message.text
    validar = False
    if resp[2] == ':':
        hora = int(resp[0]) * 10 + int(resp[1])
        mint = int(resp[3]) * 10 + int(resp[4])
        try:
            h = datetime.time(hora, mint)
            validar = True
        except:
            validar = False
    if validar == True:
        ID = chat_data['IDAtual']
        remedio = chat_data['ListaRemedio'][ID]
        remedio['hora'] = h
        chat_data['ListaRemedio'][ID] = remedio

        keyboard = [['Remedio', 'Dose'], ['Data', 'Repeticao', 'Voltar']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Voce quer alterar mais algum dado?',
                        reply_markup=reply)
        return ALTERAR
    else:
        bot.sendMessage(chat_id = chat_id,
                        text = 'Hora invalida\nQual o horario a tomar?\nFormato: hh/mm')                
        return ALTHORA  
    
def altRepeticao(bot, update, chat_data, job_queue):
    resp = update.message.text
    if resp == 'Sim':
        keyboard = [['Por hora', 'Por dia'], ['Por semana', 'Por mes']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Qual o tipo de repeticao?',
                        reply_markup=reply)
        return ALTTIPO
    elif resp == 'Nao':
        ID = chat_data['IDAtual']
        remedio = chat_data['ListaRemedio'][ID]
        remedio['repeticao']['tipo'] = 'nao'
        remedio['job'].schedule_removal()
        A = remedio['data'].year
        M = remedio['data'].month
        D = remedio['data'].day
        h = remedio['hora'].hour
        m = remedio['hora'].minute
        data = datetime.datetime(year=A, month=M, day=D, hour=h, minute=m)
        contexto = {}
        contexto['remedio'] = remAtual
        contexto['chat_id'] = update.message.chat_id
        now = datetime.datetime.now()
        intervalo = (data-now).total_seconds()
        job = Job(alarme, interval=intervalo, repeat=False, context=contexto)
        job_queue._put(job)
        remedio['job'] = job
        chat_data['ListaRemedio'][ID] = remedio
        keyboard = [['Remedio', 'Dose'], ['Data', 'Hora', 'Voltar']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Voce quer alterar mais algum dado?',
                        reply_markup=reply)
        return ALTERAR
    else:
        keyboard = [['Sim', 'Nao']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Opcao invalida!!\nO alarme deve repetir?',
                        reply_markup=reply)
        return ALTREPETICAO

def altTipo(bot, update):
    resp = update.message.text
    opcoes = {'Por hora', 'Por dia', 'Por semana', 'Por mes'}
    if resp in opcoes:
        if resp == 'Por hora':
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='A cada quantas horas?')
            return ALTPHORA
        if resp == 'Por dia':
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='A cada quantos dias?')
            return ALTPDIA
        if resp == 'Por semana':
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='A cada quantas semanas?')
            return ALTPSEMANA
        if resp == 'Por mes':
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='A cada quantos meses?')
            return ALTPMES
    else:
        keyboard = [['Por hora', 'Por dia'], ['Por semana', 'Por mes']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Opcao invalida!!\nQual o tipo de repeticao?',
                        reply_markup=reply)
        return ALTTIPO

def altPHora(bot, update, chat_data, job_queue):
    resp = update.message.text
    try:
        resp = int(resp)
        ID = chat_data['IDAtual']
        remedio = chat_data['ListaRemedio'][ID]
        remedio['repeticao']['tipo'] = 'hora(s)'
        remedio['repeticao']['aCada'] = resp
        A = remedio['data'].year
        M = remedio['data'].month
        D = remedio['data'].day
        h = remedio['hora'].hour
        m = remedio['hora'].minute
        data = datetime.datetime(year=A, month=M, day=D, hour=h, minute=m)
        contexto = {}
        contexto['remedio'] = remedio
        contexto['chat_id'] = update.message.chat_id
        remedio['job'].schedule_removal()
        remedio['job'] = job_queue.run_repeating(alarme, remAtual['repeticao']['aCada']*3600, first=data, context=contexto, name=None)
        chat_data['ListaRemedio'][ID] = remedio
        keyboard = [['Remedio', 'Dose'], ['Data', 'Hora', 'Voltar']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Voce quer alterar mais algum dado?',
                        reply_markup=reply)
        return ALTERAR
    except:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Opcao invalida!!\nA cada quantas horas?')
        return ALTPHORA
    
def altPDia(bot, update, chat_data, job_queue):
    resp = update.message.text
    try:
        resp = int(resp)
        ID = chat_data['IDAtual']
        remedio = chat_data['ListaRemedio'][ID]
        remedio['repeticao']['tipo'] = 'dia(s)'
        remedio['repeticao']['aCada'] = resp
        A = remedio['data'].year
        M = remedio['data'].month
        D = remedio['data'].day
        h = remedio['hora'].hour
        m = remedio['hora'].minute
        data = datetime.datetime(year=A, month=M, day=D, hour=h, minute=m)
        contexto = {}
        contexto['remedio'] = remedio
        contexto['chat_id'] = update.message.chat_id
        remedio['job'].schedule_removal()
        remedio['job'] = job_queue.run_repeating(alarme, remAtual['repeticao']['aCada']*86400, first=data, context=contexto, name=None)
        chat_data['ListaRemedio'][ID] = remedio
        keyboard = [['Remedio', 'Dose'], ['Data', 'Hora', 'Voltar']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Voce quer alterar mais algum dado?',
                        reply_markup=reply)
        return ALTERAR
    except:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Opcao invalida!!\nA cada quantos dias?')
        return ALTPDIA
    
def altPSemana(bot, update, chat_data, job_queue):
    resp = update.message.text
    try:
        resp = int(resp)
        ID = chat_data['IDAtual']
        remedio = chat_data['ListaRemedio'][ID]
        remedio['repeticao']['tipo'] = 'semana(s)'
        remedio['repeticao']['aCada'] = resp
        A = remedio['data'].year
        M = remedio['data'].month
        D = remedio['data'].day
        h = remedio['hora'].hour
        m = remedio['hora'].minute
        data = datetime.datetime(year=A, month=M, day=D, hour=h, minute=m)
        contexto = {}
        contexto['remedio'] = remedio
        contexto['chat_id'] = update.message.chat_id
        remedio['job'].schedule_removal()
        remedio['job'] = job_queue.run_repeating(alarme, remAtual['repeticao']['aCada']*604800, first=data, context=contexto, name=None)
        chat_data['ListaRemedio'][ID] = remedio
        keyboard = [['Remedio', 'Dose'], ['Data', 'Hora', 'Voltar']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Voce quer alterar mais algum dado?',
                        reply_markup=reply)
        return ALTERAR
    except:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Opcao invalida!!\nA cada quantas semanas?')
        return ALTPSEMANA
    
def altPMes(bot, update, chat_data, job_queue):
    resp = update.message.text
    try:
        resp = int(resp)
        ID = chat_data['IDAtual']
        remedio = chat_data['ListaRemedio'][ID]
        remedio['repeticao']['tipo'] = 'mes(es)'
        remedio['repeticao']['aCada'] = resp
        A = remedio['data'].year
        M = remedio['data'].month
        D = remedio['data'].day
        h = remedio['hora'].hour
        m = remedio['hora'].minute
        data = datetime.datetime(year=A, month=M, day=D, hour=h, minute=m)
        contexto = {}
        contexto['remedio'] = remedio
        contexto['chat_id'] = update.message.chat_id
        remedio['job'].schedule_removal()
        remedio['job'] = job_queue.run_repeating(alarme, remAtual['repeticao']['aCada']*2592000, first=data, context=contexto, name=None)
        chat_data['ListaRemedio'][ID] = remedio
        keyboard = [['Remedio', 'Dose'], ['Data', 'Hora', 'Voltar']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Voce quer alterar mais algum dado?',
                        reply_markup=reply)
        return ALTERAR
    except:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Opcao invalida!!\nA cada quantos meses?')
        return ALTPMES
    
def alterar(bot, update, chat_data):
    chat_id = update.message.chat_id
    resp = update.message.text
    opcoes = {'Remedio', 'Dose', 'Data', 'Hora', 'Repeticao', 'Voltar'}
    if resp in opcoes:
        if resp == 'Remedio':
            bot.sendMessage(chat_id=chat_id,
                            text='Qual novo nome do remedio?')
            return ALTREMEDIO
        if resp == 'Dose':
            bot.sendMessage(chat_id=chat_id,
                            text='Qual nova dose do remedio?')
            return ALTDOSE
        if resp == 'Data':
            bot.sendMessage(chat_id=chat_id,
                            text='Qual nova data do alarme?\nFormato: DD/MM/AAAA')
            return ALTDATA
        if resp == 'Hora':
            bot.sendMessage(chat_id=chat_id,
                            text='Qual nova hora do alarme?')
            return ALTHORA
        if resp == 'Repeticao':
            keyboard = [['Sim', 'Nao']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, on_time_keyboard=True)
            bot.sendMessage(chat_id=chat_id,
                            text='O alarme deve repetir?',
                            reply_markup=reply)
            return ALTREPETICAO
        if resp == 'Voltar':
            ListaRemedio = chat_data['ListaRemedio']

            for x in range(1, chat_data['QtdR']+1):
                R = ListaRemedio[x]
                data = R['data']
                hora = R['hora']
                d2 = datetime.datetime(year=data.year, month=data.month, day=data.day, hour=hora.hour, minute=hora.minute)
                now = datetime.datetime.now()
                if (d2 - now).total_seconds() <= 0:
                    for y in range(x, chat_data['QtdR']):
                        ListaRemedio[y] = ListaRemedio[y+1]
                    chat_data['QtdR'] -= 1

            if chat_data['QtdR'] == 0:
                bot.sendMessage(chat_id = chat_id,
                                text = 'Voce nao tem remedio na lista')
                keyboard = [['Adicionar remedio'],['Listar remedios']]
                reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                bot.sendMessage(chat_id=chat_id,
                                text='Em que posso ajudar?',
                                reply_markup=reply)
                return INI

            bot.sendMessage(chat_id=chat_id,
                            text='Voce tem %d alarme(s)' % chat_data['QtdR'])
            
            for x in range(1, chat_data['QtdR']+1):
                R = ListaRemedio[x]
                if R['repeticao']['tipo'] == 'nao':
                    bot.sendMessage(chat_id = chat_id,
                                    text='ID: %d, Remedio: %s, Dose: %s, Data: %s, Hora: %s, Sem repeticao' % (x, R['remedio'], R['dose'], R['data'], R['hora']))
                else:
                    bot.sendMessage(chat_id = chat_id,
                                    text='ID: %d, Remedio: %s, Dose: %s, Data inicio: %s, Hora: %s, Repeticao: a cada %d %s' %(x, R['remedio'], R['dose'], R['data'], R['hora'], R['repeticao']['aCada'], R['repeticao']['tipo']))

            chat_data['ListaRemedio'] = ListaRemedio
            
            keyboard=[['Voltar']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=chat_id,
                            text='Digite ID do alarme que deseja alterar ou deletar\nOu pressione o botao Voltar',
                            reply_markup=reply)
            return LISTA1
    else:
        keyboard = [['Remedio', 'Dose', 'Data'], ['Hora', 'Repeticao', 'Voltar']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Opcao invalida!!\nQual dado do alarme voce quer alterar?',
                        reply_markup=reply)
        return ALTERAR
        
def deletar(bot, update, chat_data):
    resp = update.message.text
    opcoes = {'Sim', 'Nao'}
    if resp in opcoes:
        if resp == 'Sim':
            ListaRemedio = chat_data['ListaRemedio']
            ID = chat_data['IDAtual']
            ListaRemedio[ID]['job'].schedule_removal()
            for x in range(ID, chat_data['QtdR']):
                ListaRemedio[x] = ListaRemedio[x+1]
            chat_data['QtdR'] -= 1
            chat_data['ListaRemedio'] = ListaRemedio
            del chat_data['IDAtual']
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Alarme deletado!!')
            keyboard = [['Adicionar remedio'],['Listar remedios']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Em que posso ajudar?',
                            reply_markup=reply)
            return INI
        if resp == 'Nao':
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Operacao cancelada!')
            keyboard = [['Adicionar remedio'],['Listar remedios']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Em que posso ajudar?',
                            reply_markup=reply)
            return INI
    else:
        keyboard = [['Sim', 'Nao']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id = update.message.chat_id,
                        text='Opcao invalida!!\nTem certeza que quer deletar o alarme escolhido?',
                        reply_markup=reply)
        return deletar

def remedio(bot, update, chat_data):
    chat_id = update.message.chat_id
    resp = update.message.text
    remAtual={}
    remAtual['remedio'] = resp
    chat_data['remAtual'] = remAtual
    bot.sendMessage(chat_id=chat_id,
                    text='Remedio: %s\nQual a dose?' % remAtual['remedio'])
    return DOSE
    
def dose(bot, update, chat_data):
    chat_id = update.message.chat_id
    resp = update.message.text
    remAtual = chat_data['remAtual']
    remAtual['dose'] = resp
    chat_data['remAtual'] = remAtual
    bot.sendMessage(chat_id = chat_id,
                    text = 'Remedio: %s, Dose: %s\nQual o dia a tomar?\nFormato: DD/MM/AAAA' %(remAtual['remedio'], remAtual['dose']))
    return DIA

def dia(bot, update, chat_data):
    chat_id = update.message.chat_id
    resp = update.message.text
    validar = False
    if len(resp) <= 2:
        if len(resp) == 1:
            try:
                dia = int(resp[0])
                validar = True
            except:
                validar = False
        elif len(resp) == 2:
            try:
                dia = int(resp[0]) * 10 + int(resp[1])
                validar = True
            except:
                validar = False
        if validar:
            mes = datetime.datetime.now().month
            ano = datetime.datetime.now().year
    elif len(resp) == 5:
        try:
            dia = int(resp[0]) * 10 + int(resp[1])
            mes = int(resp[3]) * 10 + int(resp[4])
            ano = datetime.datetime.now().year
        except:
            validar = False
    else:
        try:
            dia = int(resp[0]) * 10 + int(resp[1])
            mes = int(resp[3]) * 10 + int(resp[4])
            ano = int(resp[6]) * 1000 + int(resp[7]) * 100 + int(resp[8]) * 10 + int(resp[9])
        except:
            validar = False

    try:
        data = datetime.date(ano, mes, dia)
        validar = True
    except:
        validar = False

    if validar == True:
        remAtual = chat_data['remAtual']
        remAtual['data'] = data
        chat_data['remAtual'] = remAtual
        bot.sendMessage(chat_id=chat_id,
                        text = 'Remedio: %s, Dose: %s, Dia: %s\nQual o horario a tomar?\nFormato: hh:mm' %(remAtual['remedio'], remAtual['dose'], remAtual['data']))
        return HORA
    else:
        bot.sendMessage(chat_id = chat_id,
                            text = 'Data invalida\nQual o dia a tomar?\nFormato: DD/MM/AAAA')                
        return DIA       
   
def hora(bot, update, chat_data):
    chat_id = update.message.chat_id
    resp = update.message.text
    validar = False
    if resp[2] == ':':
        hora = int(resp[0]) * 10 + int(resp[1])
        mint = int(resp[3]) * 10 + int(resp[4])
        try:
            h = datetime.time(hora, mint)
            validar = True
        except:
            validar = False
            
    if validar == True:
        remAtual = chat_data['remAtual']
        remAtual['hora'] = h
        chat_data['remAtual'] = remAtual
        keyboard = [['Sim','Nao']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard = True, one_time_keyboard = True)
        bot.sendMessage(chat_id=chat_id,
                        text = 'Remedio: %s, Dose: %s, Dia: %s, Hora: %s\nRepetir?' % (remAtual['remedio'],remAtual['dose'], remAtual['data'], remAtual['hora']),
                        reply_markup = reply)
        return REPETICAO
    else:
        bot.sendMessage(chat_id = chat_id,
                        text = 'Hora invalida\nQual o horario a tomar?\nFormato: hh/mm')                
        return HORA

def repeticao(bot, update, groups, chat_data, job_queue):
    chat_id = update.message.chat_id
    opcao = groups[0]
    opcoes = {'Sim', 'Nao'}
    if opcao in opcoes:
        if opcao == 'Nao':
            remAtual = chat_data['remAtual']
            remAtual['repeticao']={}
            remAtual['repeticao']['tipo'] = 'nao'
            chat_data['remAtual'] = remAtual

            bot.sendMessage(chat_id = chat_id,
                            text='Remedio: %s, Dose: %s, Dia: %s, Hora: %s\nSem repeticao' % (remAtual['remedio'],remAtual['dose'], remAtual['data'], remAtual['hora']))
            keyboard = [['Sim', 'Nao']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id = update.message.chat_id,
                            text='Tem certeza que quer finalizar?',
                            reply_markup=reply)
            return FIM
        else:
            keyboard = [['Por hora', 'Por dia'],
                        ['Por semana', 'Por mes']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=chat_id,
                            text='Tipo de repeticao',
                            reply_markup=reply)
            return TIPO
    else:
        keyboard = ['Sim','Nao']
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard = True, one_time_keyboard = True)
        bot.sendMessage(chat_id=chat_id,
                        text = 'Escolha invalida!\nRepetir?',
                        reply_markup = reply)
        return REPETICAO
                        
def tipo(bot, update):
    chat_id = update.message.chat_id
    opcao = update.message.text
    opcoes = {'Por hora', 'Por dia', 'Por semana', 'Por mes'}
    if opcao in opcoes:
        if opcao == 'Por hora':
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='A cada quantas horas?')
            return PORH
        if opcao == 'Por dia':
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='A cada quantos dias?')
            return PORD
        if opcao == 'Por semana':
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='A cada quantas semanas?')
            return PORS
        if opcao == 'Por mes':
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='A cada quantos meses?')
            return PORM
    else:
        keyboard = [['Por hora', 'Por dia'],
                    ['Por semana', 'Por mes']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=chat_id,
                        text='Escolha invalida!!\nQual o tipo de repeticao',
                        reply_markup=reply)
        return TIPO
    
def porH(bot, update, chat_data):
    resp = int(update.message.text)
    if resp > 0 and resp < 24:
        repeticao = {}
        repeticao['tipo'] = 'hora(s)'
        repeticao['aCada'] = resp
        remAtual = chat_data['remAtual']
        remAtual['repeticao'] = repeticao
        chat_data['remAtual'] = remAtual
        bot.sendMessage(chat_id = update.message.chat_id,
                        text='Remedio: %s, Dose: %s, Dia: %s, Hora: %s\nRepeticao: a cada %d %s' % (remAtual['remedio'],remAtual['dose'], remAtual['data'], remAtual['hora'], remAtual['repeticao']['aCada'], remAtual['repeticao']['tipo']))
        keyboard = [['Sim', 'Nao']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id = update.message.chat_id,
                        text='Tem certeza que quer finalizar?',
                        reply_markup=reply)
        return FIM
    else:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Digite valor de 1 a 23\nRepetir a cada quantas horas?')
        return PORH
            
def porD(bot, update, chat_data):
    resp = int(update.message.text)
    repeticao = {}
    repeticao['tipo'] = 'dia(s)'
    repeticao['aCada'] = resp
    remAtual = chat_data['remAtual']
    remAtual['repeticao'] = repeticao
    chat_data['remAtual'] = remAtual
    bot.sendMessage(chat_id = update.message.chat_id,
                    text='Remedio: %s, Dose: %s, Dia: %s, Hora: %s\nRepeticao: a cada %d %s' % (remAtual['remedio'],remAtual['dose'], remAtual['data'], remAtual['hora'], remAtual['repeticao']['aCada'], remAtual['repeticao']['tipo']))
    keyboard = [['Sim', 'Nao']]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    bot.sendMessage(chat_id = update.message.chat_id,
                    text='Tem certeza que quer finalizar?',
                    reply_markup=reply)
    return FIM

def porS(bot, update, chat_data):
    resp = int(update.message.text)
    repeticao = {}
    repeticao['tipo'] = 'semana(s)'
    repeticao['aCada'] = resp
    remAtual = chat_data['remAtual']
    remAtual['repeticao'] = repeticao
    chat_data['remAtual'] = remAtual
    bot.sendMessage(chat_id = update.message.chat_id,
                    text='Remedio: %s, Dose: %s, Dia: %s, Hora: %s\nRepeticao: a cada %d %s' % (remAtual['remedio'],remAtual['dose'], remAtual['data'], remAtual['hora'], remAtual['repeticao']['aCada'], remAtual['repeticao']['tipo']))
    keyboard = [['Sim', 'Nao']]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    bot.sendMessage(chat_id = update.message.chat_id,
                    text='Tem certeza que quer finalizar?',
                    reply_markup=reply)
    return FIM

def porM(bot, update, chat_data):
    resp = int(update.message.text)
    repeticao = {}
    repeticao['tipo'] = 'mes(es)'
    repeticao['aCada'] = resp
    remAtual = chat_data['remAtual']
    remAtual['repeticao'] = repeticao
    chat_data['remAtual'] = remAtual
    bot.sendMessage(chat_id = update.message.chat_id,
                    text='Remedio: %s, Dose: %s, Dia: %s, Hora: %s\nRepeticao: a cada %d %s' % (remAtual['remedio'],remAtual['dose'], remAtual['data'], remAtual['hora'], remAtual['repeticao']['aCada'], remAtual['repeticao']['tipo']))
    keyboard = [['Sim', 'Nao']]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    bot.sendMessage(chat_id = update.message.chat_id,
                    text='Tem certeza que quer finalizar?',
                    reply_markup=reply)
    return FIM

def fim(bot, update, chat_data, job_queue):
    remAtual = chat_data['remAtual']
    opcao = update.message.text
    opcoes = {'Sim', 'Nao'}
    if opcao in opcoes:
        if opcao == 'Sim':
            if remAtual['repeticao']['tipo'] == 'nao':
                bot.sendMessage(chat_id = update.message.chat_id,
                                text='Remedio: %s, Dose: %s, Dia: %s, Hora: %s\nSem repeticao'
                                % (remAtual['remedio'],remAtual['dose'], remAtual['data'], remAtual['hora']))
            else:
                bot.sendMessage(chat_id = update.message.chat_id,
                                text='Remedio: %s, Dose: %s, Dia: %s, Hora: %s\nRepeticao: a cada %d %s'
                                % (remAtual['remedio'],remAtual['dose'], remAtual['data'], remAtual['hora'], remAtual['repeticao']['aCada'], remAtual['repeticao']['tipo']))
                bot.sendMessage(chat_id = update.message.chat_id,
                                text='Remedio adicionado na lista!')
            A = remAtual['data'].year
            M = remAtual['data'].month
            D = remAtual['data'].day
            h = remAtual['hora'].hour
            m = remAtual['hora'].minute
            data = datetime.datetime(year=A, month=M, day=D, hour=h, minute=m)
            contexto = {}
            contexto['remedio'] = remAtual
            contexto['chat_id'] = update.message.chat_id
            repeticao = remAtual['repeticao']
            if repeticao['tipo'] == 'hora(s)':
                job = job_queue.run_repeating(alarme, remAtual['repeticao']['aCada']*3600, first=data, context=contexto, name=None)
                remAtual['job'] = job
            if repeticao['tipo'] == 'dia(s)':
                job = job_queue.run_repeating(alarme, remAtual['repeticao']['aCada']*86400, first=data, context=contexto, name=None)
                remAtual['job'] = job
            if repeticao['tipo'] == 'semana(s)':
                job = job_queue.run_repeating(alarme, remAtual['repeticao']['aCada']*604800, first=data, context=contexto, name=None)
                remAtual['job'] = job
            if repeticao['tipo'] == 'mes(es)':
                job = job_queue.run_repeating(alarme, remAtual['repeticao']['aCada']*2592000, first=data, context=contexto, name=None)
                remAtual['job'] = job
            if repeticao['tipo'] == 'nao':
                now = datetime.datetime.now()
                intervalo = (data-now).total_seconds()
                job = Job(alarme, interval=intervalo, repeat=False, context=contexto)
                job_queue._put(job)
                remAtual['job'] = job
                
            q = chat_data['QtdR']
            q = q + 1
            chat_data['QtdR'] = q
            ListaRemedio = chat_data['ListaRemedio']
            ListaRemedio[q] = remAtual
            chat_data['ListaRemedio'] = ListaRemedio
            del chat_data['remAtual']
            keyboard = [['Adicionar remedio'],['Listar remedios']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='O que voce quer fazer?',
                            reply_markup=reply)
            return INI
        else:            
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Operacao cancelada!')
            keyboard = [['Adicionar remedio'],['Listar remedios']]
            reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Em que posso ajudar?',
                            reply_markup=reply)
            return INI
    else:
        keyboard = [['Sim', 'Nao']]
        reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Opcao invalida!')
        bot.sendMessage(chat_id = update.message.chat_id,
                        text='Remedio: %s, Dose: %s, Dia: %s, Hora: %s\nRepeticao: a cada %d %s' % (remAtual['remedio'],remAtual['dose'], remAtual['data'], remAtual['hora'], remAtual['repeticao']['aCada'], remAtual['repeticao']['tipo']))
        bot.sendMessage(chat_id = update.message.chat_id,
                        text='Opcao invalida!!\nTem certeza que quer finalizar?',
                        reply_markup=reply)
        
def cancel(bot, update, chat_data):
    bot.sendMessage(chat_id= update.message.chat_id,
                    text='Operacao Cancelada')
    if 'remAtual' in chat_data:
        del chat_data['remAtual']

    keyboard = [['Adicionar remedio'],['Listar remedios']]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    bot.sendMessage(chat_id=chat_id,
                    text='Em que posso ajudar?',
                    reply_markup=reply)
    return INI

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
        
def alarme(bot, job):
    contexto = job.context
    remedio = contexto['remedio']
    chat_id = contexto['chat_id']
    bot.sendMessage(chat_id = chat_id,
                    text='Alarme3\nAlerta para tomar remedio!!\nRemedio: %s, Dose: %s' %(remedio['remedio'], remedio['dose']))
    
def main():
    updater = Updater("363455140:AAHToRxLbqGU-JlhXt-sysZ3nAAF_Uq_GGo")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, pass_chat_data=True))
    dp.add_handler(CommandHandler("help", start))
    convH_add = ConversationHandler(
        entry_points=[RegexHandler('^(Adicionar remedio|Listar remedios)$', key_select_oquefazer, pass_groups=True, pass_chat_data=True)],
        states={
            REMEDIO:    [MessageHandler(Filters.text, remedio, pass_chat_data=True)],
            DOSE:       [MessageHandler(Filters.text, dose, pass_chat_data=True)],
            DIA:        [MessageHandler(Filters.text, dia, pass_chat_data=True)],
            HORA:       [MessageHandler(Filters.text, hora, pass_chat_data=True)],
            REPETICAO:  [RegexHandler('^(Sim|Nao)$', repeticao, pass_chat_data=True, pass_groups=True, pass_job_queue=True)],

            TIPO:       [RegexHandler('^(Por hora|Por dia|Por semana|Por mes)$', tipo)],
                       
            PORH:       [MessageHandler(Filters.text, porH, pass_chat_data=True)],
            PORD:       [MessageHandler(Filters.text, porD, pass_chat_data=True)],
            PORS:       [MessageHandler(Filters.text, porS, pass_chat_data=True)],
            PORM:       [MessageHandler(Filters.text, porM, pass_chat_data=True)],
            FIM:        [MessageHandler(Filters.text, fim, pass_chat_data=True, pass_job_queue=True)],
            INI:        [RegexHandler('^(Adicionar remedio|Listar remedios)$', key_select_oquefazer, pass_groups=True, pass_chat_data=True)],

            LISTA1:     [MessageHandler(Filters.text, lista1, pass_chat_data=True)],
            LISTA2:     [RegexHandler('^(Alterar|Deletar|Voltar)$', lista2, pass_chat_data=True)],
            DELETAR:    [RegexHandler('^(Sim|Nao)$', deletar, pass_chat_data=True)],

            ALTERAR:    [RegexHandler('^(Remedio|Dose|Data|Hora|Repeticao|Voltar)$', alterar, pass_chat_data=True)],
            ALTREMEDIO: [MessageHandler(Filters.text, altRemedio, pass_chat_data=True)],
            ALTDOSE:    [MessageHandler(Filters.text, altDose, pass_chat_data=True)],
            ALTDATA:    [MessageHandler(Filters.text, altData, pass_chat_data=True)],
            ALTHORA:    [MessageHandler(Filters.text, altHora, pass_chat_data=True)],
            ALTREPETICAO:[RegexHandler('^(Sim|Nao)$', altRepeticao, pass_chat_data=True, pass_job_queue=True)],
            ALTPHORA:    [MessageHandler(Filters.text, altPHora, pass_chat_data=True, pass_job_queue=True)],
            ALTPDIA:     [MessageHandler(Filters.text, altPDia, pass_chat_data=True, pass_job_queue=True)],
            ALTPSEMANA:  [MessageHandler(Filters.text, altPSemana, pass_chat_data=True, pass_job_queue=True)],
            ALTPMES:     [MessageHandler(Filters.text, altPMes, pass_chat_data=True, pass_job_queue=True)]
        },
        
        fallbacks = [CommandHandler('cancel', cancel, pass_chat_data=True)]
    )

    dp.add_handler(convH_add)
    
    dp.add_error_handler(error)

    updater.start_polling()
                   
    updater.idle()


if __name__ == '__main__':
    main()
