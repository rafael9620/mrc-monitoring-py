#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime
import schedule
import requests
from emoji import emojize
import psutil
import MySQLdb
import logging


logger = logging.getLogger('dediti-scripts')
hdlr = logging.FileHandler('/opt/logs/dediti-scripts.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
logger.info('Iniciando ...')
last_minutes = 30

# -1001268009061
# 631982296


def telegram_bot_sendtext(bot_message):
    bot_token = '1201834384:AAHdz3ayeO9E4GUIXx63nJOhyH70lAZ5syQ'
    bot_chatID = '-1001268009061'
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Html&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


def elastichealth():
    critical = False
    bell = emojize(":bell:", use_aliases=True)
    msg = bell + \
        " <b>Elasticsearch</b> (<i>{}</i>)\n       <b>cluster: </b> {}\n       <b> status: </b> {}\n       <b>  nodes: </b> {}"
    ELASTIC_HOST = "http://localhost:9200"
    try:
        r = requests.get(ELASTIC_HOST + '/_cluster/health')
        logger.info('Chequeando a Elasticsearch ...')
        logger.info("STATUS CODE: " + str(r.status_code))
        if(r.status_code == requests.codes.ok):
            data = r.json()
            status = data['status']
            cluster = data['cluster_name']
            number_of_nodes = data['number_of_nodes']
            unassigned_shards = data['unassigned_shards']
            active_primary_shards = data['active_primary_shards']
            status_ = "WARN"
            if(status == "green"):
                status_ = "SUCCESS"
            if(status == "red"):
                status_ = "CRITICAL"

            if(status_ == "CRITICAL"):
                critical = True

            logger.info("STATUS: " + str(status_))
            msg = msg.format("UP", cluster, status_, number_of_nodes)
        else:
            critical = True
            msg = msg.format("DOWN", "-", "CRITICAL", "-")
    except requests.ConnectionError:
        logger.error("[ERROR] - requests.ConnectionError")
        critical = True
        msg = msg.format("DOWN", "-", "CRITICAL", "-")

    if(critical):
        logger.error("[ERROR] - " + msg)
        return msg
    else:
        return ""


def apihealth():
    critical = False
    bell = emojize(":bell:", use_aliases=True)
    msg = bell + \
        " <b>Dediti Backend</b> (<i>{}</i>)\n       <b>elasticsearch: </b> {}\n       <b>            mysql: </b> {}"
    API_HOST = "http://localhost:7007"
    try:
        r = requests.get(API_HOST + '/actuator/health')
        logger.info('Chequeando a Dediti Backend ...')
        logger.info("STATUS CODE: " + str(r.status_code))
        if(r.status_code == requests.codes.ok or r.status_code == 503):
            data = r.json()
            status = data['status']
            elasticsearch = data['components']['elasticsearch']['status']
            mysql = data['components']['db']['status']
            if(status == "DOWN" or elasticsearch == "DOWN" or mysql == "DOWN"):
                critical = True
            logger.info("STATUS: " + str(status))
            msg = msg.format(status, elasticsearch, mysql)
        else:
            critical = True
            msg = msg.format("DOWN", "-", "-")
    except requests.ConnectionError:
        logger.error("[ERROR] - requests.ConnectionError")
        critical = True
        msg = msg.format("DOWN", "-", "-")

    if(critical):
        logger.error("[ERROR] - " + msg)
        return msg
    else:
        return ""


def message():
    rotating_light = emojize(":rotating_light:", use_aliases=True)
    error = rotating_light + " <b>CRITICAL ALERT</b> " + rotating_light
    elastic = elastichealth()
    api = apihealth()
    if(api != ""):
        api = "\n" + api
    if(elastic != ""):
        elastic = "\n" + elastic
    message = error + "\n" + api + "\n" + elastic
    if(api != "" or elastic != ""):
        # print(message)
        telegram_bot_sendtext(message)


def resources():
    part_alternation_mark = emojize(
        ":part_alternation_mark:", use_aliases=True)
    black_small_square = emojize(":black_small_square:", use_aliases=True)
    small_blue_diamond = emojize(":small_blue_diamond:", use_aliases=True)
    hdd_ = psutil.disk_usage('/')
    resources = part_alternation_mark + " <b>SERVER RESOURCES</b> "
    cpu = "    " + small_blue_diamond + \
        " <b>CPU: </b>" + str(psutil.cpu_percent()) + " %"
    ram = "    " + small_blue_diamond + " <b>RAM: </b>" + \
        str(psutil.virtual_memory().percent) + " %"
    hdd = "    " + small_blue_diamond + " <b>HDD (/):</b>"
    hto = "         " + black_small_square + \
        " total: " + str(hdd_.total / (2**30)) + " GiB"
    hus = "         " + black_small_square + \
        " usado: " + str(hdd_.used / (2**30)) + " GiB"
    hfr = "         " + black_small_square + \
        " libre: " + str(hdd_.free / (2**30)) + " GiB"
    message = resources + "\n\n" + cpu + "\n" + ram + \
        "\n" + hdd + "\n" + hto + "\n" + hus + "\n" + hfr
    return message


def offers():
    ELASTIC_HOST = "http://localhost:9200"
    try:
        r = requests.get(ELASTIC_HOST + '/offers/_count')
        if(r.status_code == requests.codes.ok):
            data = r.json()
            count = data['count']
            return count
    except requests.ConnectionError:
        return 0
    return 0


def stats():
    bar_chart = emojize(":bar_chart:", use_aliases=True)
    black_small_square = emojize(":black_small_square:", use_aliases=True)
    small_blue_diamond = emojize(":small_blue_diamond:", use_aliases=True)
    db = MySQLdb.connect("dbprod.sacavix.com", "mailu",
                         "4HUaM9pF9OF2", "offersapi")
    stats = bar_chart + " <b>DEDITI STATS</b> "
    offer = "    " + small_blue_diamond + " <b>Offers:</b> " + str(offers())
    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.alert;")
    data = cursor.fetchone()
    alerts = "    " + small_blue_diamond + " <b>Alerts:</b> " + str(data[0])
    cursor.execute("SELECT count(*) FROM offersapi.categories;")
    data = cursor.fetchone()
    categories = "    " + small_blue_diamond + \
        " <b>Categories:</b> " + str(data[0])
    cursor.execute("SELECT count(*) FROM offersapi.currency;")
    data = cursor.fetchone()
    currency = "    " + small_blue_diamond + \
        " <b>Currencies:</b> " + str(data[0])
    cursor.execute("SELECT count(*) FROM offersapi.report;")
    data = cursor.fetchone()
    report = "    " + small_blue_diamond + " <b>Reports:</b> " + str(data[0])
    message = stats + "\n\n" + offer + "\n" + alerts + \
        "\n" + categories + "\n" + currency + "\n" + report
    return message


def operations():
    db = MySQLdb.connect("dbprod.sacavix.com", "mailu",
                         "4HUaM9pF9OF2", "offersapi")
    chart_with_upwards_trend = emojize(
        ":chart_with_upwards_trend:", use_aliases=True)
    black_small_square = emojize(":black_small_square:", use_aliases=True)
    small_blue_diamond = emojize(":small_blue_diamond:", use_aliases=True)

    stats = chart_with_upwards_trend + \
        " <b>APIs STATS</b> <i>(last " + str(last_minutes) + " minutes)</i> "

    cursor = db.cursor()
    cursor.execute("select count(*) FROM operation WHERE operation.created_at > (now() - interval " +
                   str(last_minutes) + " minute ) ;")
    data = cursor.fetchone()
    operations = "   " + small_blue_diamond + \
        " <b>Operations:</b> " + str(data[0])

    cursor.execute("SELECT avg(operation.response_time) FROM offersapi.operation WHERE operation.created_at > (now() - interval " +
                   str(last_minutes) + " minute );")
    data = cursor.fetchone()
    if(data[0] is None):
        data = "-"
    else:
        data = str(round(data[0], 2)) + "s"
    time_response_avg = "   " + small_blue_diamond + \
        " <b>Time Response Avg:</b> " + str(data)

    https_codes = "   " + small_blue_diamond + " <b>Response Codes:</b> "
    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.operation WHERE operation.code_response >= 200 AND operation.code_response <= 299 AND operation.created_at > (now() - interval " + str(last_minutes) + " minute );")
    data = cursor.fetchone()
    c2xx = "         " + black_small_square + " 2xx: " + str(data[0])

    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.operation WHERE operation.code_response >= 300 AND operation.code_response <= 399 AND operation.created_at > (now() - interval " + str(last_minutes) + " minute );")
    data = cursor.fetchone()
    c3xx = "         " + black_small_square + " 3xx: " + str(data[0])

    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.operation WHERE operation.code_response >= 400 AND operation.code_response <= 499 AND operation.created_at > (now() - interval " + str(last_minutes) + " minute );")
    data = cursor.fetchone()
    c4xx = "         " + black_small_square + " 4xx: " + str(data[0])

    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.operation WHERE operation.code_response >= 500 AND operation.code_response <= 599 AND operation.created_at > (now() - interval " + str(last_minutes) + " minute );")
    data = cursor.fetchone()
    c5xx = "         " + black_small_square + " 5xx: " + str(data[0])

    methods = "   " + small_blue_diamond + " <b>Methods:</b> "
    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.operation WHERE operation.method='POST' AND operation.created_at > (now() - interval " +
                   str(last_minutes) + " minute ) group by method;")
    data = cursor.fetchone()
    if data is None:
        data = 0
    else:
        data = data[0]
    post = "         " + black_small_square + " POST: " + str(data)

    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.operation WHERE operation.method='GET' AND operation.created_at > (now() - interval " +
                   str(last_minutes) + " minute ) group by method;")
    data = cursor.fetchone()
    if data is None:
        data = 0
    else:
        data = data[0]
    get = "         " + black_small_square + " GET: " + str(data)

    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.operation WHERE operation.method='PUT' AND operation.created_at > (now() - interval " +
                   str(last_minutes) + " minute ) group by method;")
    data = cursor.fetchone()
    if data is None:
        data = 0
    else:
        data = data[0]
    put = "         " + black_small_square + " PUT: " + str(data)

    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.operation WHERE operation.method='DELETE' AND operation.created_at > (now() - interval " +
                   str(last_minutes) + " minute ) group by method;")
    data = cursor.fetchone()
    if data is None:
        data = 0
    else:
        data = data[0]
    delete = "         " + black_small_square + " DELETE: " + str(data)

    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM offersapi.operation WHERE operation.method='OPTIONS' AND operation.created_at > (now() - interval " +
                   str(last_minutes) + " minute ) group by method;")
    data = cursor.fetchone()
    if data is None:
        data = 0
    else:
        data = data[0]
    options = "         " + black_small_square + " OPTIONS: " + str(data)

    message = stats + "\n\n" + operations + "\n" + time_response_avg + "\n" + https_codes + "\n" + c2xx + "\n" + c3xx + \
        "\n" + c4xx + "\n" + c5xx + "\n" + methods + "\n" + post + \
        "\n" + get + "\n" + put + "\n" + delete + "\n" + options
    return message


def all_ok():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string + " - " + "Cheking ok services.")
    white_check_mark = emojize(":white_check_mark:", use_aliases=True)
    small_blue_diamond = emojize(":small_blue_diamond:", use_aliases=True)
    ok = white_check_mark + " <b>SERVICES OK</b> "
    elastic = elastichealth()
    api = apihealth()
    #elastic = ""
    #api = ""
    if(api == "" and elastic == ""):
        ok = white_check_mark + " <b>SERVICES OK</b> "
        backend = "    " + small_blue_diamond + " <b>Dediti Backend:</b> <i>OK</i>"
        elastic = "    " + small_blue_diamond + " <b>Elasticsearch:</b> <i>OK</i>"
        mysql = "    " + small_blue_diamond + " <b>MySQL:</b> <i>OK</i>"
        nginx = "    " + small_blue_diamond + " <b>Nginx:</b> <i>OK</i>"

        message = ok + "\n\n" + backend + "\n" + \
            elastic + "\n" + mysql + "\n" + nginx + "\n"
        message = message + "\n" + resources() + "\n\n" + stats() + \
            "\n\n" + operations()
        # print(message)
        telegram_bot_sendtext(message)


schedule.every(1).minutes.do(message)
schedule.every(last_minutes).minutes.do(all_ok)

while True:
    schedule.run_pending()
    time.sleep(1)
