# from datetime import date, datetime, timedelta
import re
import sys
import json
import argparse
import datetime
import pomasy.lib as lib
from mysql_python import MysqlPython
from _datetime import datetime
from builtins import str

class blotter:
    """ Blotter class
    
        This class wraps all the trades executed 
        in a specific period of time for a
        specific account
    """

    def __init__(self,
                 fname: str,
                 pstart: datetime, 
                 pend: datetime, aumprimus, aumucits) -> tuple:
                
                """        
                Args:
                    fname(str): location of the file which contains the fills
                    pstart(datetime): start of the period in datetime format
                    pend (datetime): end of the period in datetime format
                    
                
                Returns:
                    A tuple with the trades in the period specified
                """
  
    fname = fname.strip()
    n = int(n)
    aumprimus = float(aumprimus)
    aumucits = float(aumucits)
    
    brokersPrimus = ['ATST', 'NIBB', 'WAC3'] 
    brokersUCIT = ['BDLU'] 
    brokers2fixs = ['MS', 'MSP', 'DNBM', 'DAVY', 'LMPE', 'INTK']
    exchangeRestriction = [' RO'] 
    
    if fname[-4:] != ".xls":
        fname = fname + ".xls"
        
    pathf= 'C:\\blp\\data\\' + fname
    
    content = lib.readfile(pathf)
     
    
    target_date = datetime.datetime.now().date() - datetime.timedelta(days=n)    
    
    
    trades = {}
    
    for line in content:
        line = re.sub('"', '', line)
        line = line.split(",")

        if line[0] == 'FILL' and \
            (lib.isfloat(line[7]) or lib.isint(line[7])) and \
            (lib.isfloat(line[8]) or lib.isint(line[8])):
    
            fill_ticker  = line[1].upper() + ' ' + line[2].upper()
            fill_type    = line[3].upper()
            fill_broker  = "UBSX" if (line[6].upper() == "UBSL" and line[9].upper() == "AMORIM_CFD") else line[6].upper()
            fill_price   = float(line[7])
            fill_shares  = float(line[8]) * (1 if (fill_type=='BY' or fill_type=='BS' or fill_type=='BC') else -1)
            fill_account = "EQUUS" if "EQUUS" in line[9].upper() else line[9].upper()
            fill_date    = datetime.datetime.strptime(line[11], '%m/%d/%Y')
            fill_ccy     = line[12].upper()
            
            
            if target_date == fill_date.date():
            
                ref = fill_type + '|' + fill_ticker + '|' + fill_broker
                
                matchingPrimusBroker = [True for s in brokersPrimus if s in fill_broker]
                matchingUCITBroker = [True for s in brokersUCIT if s in fill_broker]
                matchingBroker = [True for s in brokers2fixs if s in fill_broker]
                matchingExchange = [True for s in exchangeRestriction if s in fill_ticker]
                
                tbl = ""
                isprimusanducits = False
                fill_shares_primus = fill_shares_ucits = tmpfills = 0
                
                if not matchingBroker and not matchingExchange and "UBSX" not in fill_broker \
                    and not matchingUCITBroker and not matchingPrimusBroker:
                    # LBV PRIMUS MASTER FUND and EQUUS
                    isprimusanducits = True
                    tbl = "lbv.fundtrades"
                    fill_shares_primus = int(fill_shares * (aumprimus / (aumprimus + aumucits)))
                    fill_shares_ucits  = int(fill_shares * (aumucits  / (aumprimus + aumucits)))
                    fill_shares_ucits = fill_shares_ucits + (fill_shares - (fill_shares_primus + fill_shares_ucits))
                    tmpfills = fill_shares_primus
                elif "UBSX" in fill_broker.upper():
                    # AMORIM
                    ref = ref + '|AMORIM'
                    tbl = "lbv.swaptrades"
                    tmpfills = fill_shares
                elif (matchingBroker and "EQUUS" in fill_account.upper()) or matchingUCITBroker:
                    # EQUUS
                    ref = ref + '|EQUUS'
                    tbl = "lbv.ucitstrades"
                    fill_account = "EQUUS"
                    tmpfills = fill_shares
                elif matchingBroker or matchingExchange or matchingPrimusBroker:
                    # LBV Primus Master Fund
                    ref = ref + '|PRIMUS'
                    tbl = "lbv.fundtrades"
                    tmpfills = fill_shares
                else:
                    return -1
                
                
                if ref in trades:
                    
                    if isprimusanducits:
                        ucitsref = ref + '|EQUUS'
                        tmp_total_shares = trades[ref]['shares'] + trades[ucitsref]['shares'] + \
                                            (fill_shares_primus + fill_shares_ucits)
                        
                        trades[ref]['shares'] = trades[ref]['shares'] + float(fill_shares_primus)
                        
                        trades[ref]['price'] = fill_price * (fill_shares / tmp_total_shares) + \
                                                trades[ref]['price'] * (1 - (fill_shares / tmp_total_shares))
                        
                        trades[ucitsref]['shares'] = trades[ucitsref]['shares'] + float(fill_shares_ucits)
                        trades[ucitsref]['price'] =  trades[ref]['price']
                    else:
                        trades[ref]['shares'] = trades[ref]['shares'] + float(fill_shares)
                        trades[ref]['price'] = fill_price * (fill_shares / trades[ref]['shares']) + \
                                                trades[ref]['price'] * (1 - (fill_shares / trades[ref]['shares']))
                    
                    
                else:
                              
                    sql = "SELECT (" \
                            " CASE " \
                                "WHEN sum(trd_filled) > 0 THEN 'LONG' " \
                                "WHEN sum(trd_filled) < 0 THEN 'SHORT' " \
                                "ELSE IF(" + str(tmpfills) + \
                                        " > 0, 'LONG', 'SHORT')" \
                            " END) AS position" \
                        " FROM " + tbl + \
                        " WHERE trd_ticker='" + fill_ticker + "'"
                    
                    trades[ref] = {}
                    trades[ref]['id'] = fill_date.strftime("%Y%m%d") + '-' + id_generator()
                    trades[ref]['ticker'] = fill_ticker
                    trades[ref]['type']   = 'BUY' if (fill_type=='BY' or fill_type=='BS' or fill_type=='BC') else 'SELL'
                    trades[ref]['position'] = mysql_conn.selectone(sql, '#--')
                    trades[ref]['broker'] = fill_broker
                    trades[ref]['shares'] =  tmpfills
                    trades[ref]['price']  = fill_price
                    trades[ref]['account']  = fill_account
                    trades[ref]['ccy']  = fill_ccy
                    trades[ref]['date']  = fill_date.strftime("%Y-%m-%d")
                    trades[ref]['hasucits']  = isprimusanducits
                    
                    if isprimusanducits:
                        
                        ref = ref + '|EQUUS'
                        
                        sql =   "SELECT (" \
                                    " CASE " \
                                        "WHEN sum(trd_filled) > 0 THEN 'LONG' " \
                                        "WHEN sum(trd_filled) < 0 THEN 'SHORT' " \
                                        "ELSE IF(" + str(fill_shares_ucits) + " > 0, 'LONG', 'SHORT')" \
                                    " END) AS position" \
                                " FROM lbv.ucitstrades" + \
                                " WHERE trd_ticker='" + fill_ticker + "'"
                        
                        trades[ref] = {}
                        trades[ref]['id'] = fill_date.strftime("%Y%m%d") + '-' + id_generator()
                        trades[ref]['ticker'] = fill_ticker
                        trades[ref]['type']   = 'BUY' if (fill_type=='BY' or fill_type=='BS' or fill_type=='BC') else 'SELL'
                        trades[ref]['position'] = mysql_conn.selectone(sql, '#--')
                        trades[ref]['broker'] = fill_broker
                        trades[ref]['shares'] = fill_shares_ucits
                        trades[ref]['price']  = fill_price
                        trades[ref]['account']  = 'EQUUS'
                        trades[ref]['date']  = fill_date.strftime("%Y-%m-%d")
                        trades[ref]['hasucits'] = False 
    
    # Replace the amount with the total pro rata
    # Before step was pro rata by fills
    for ref in trades:
        if trades[ref]['hasucits']:
            
            ticker = trades[ref]['ticker']
            sql = "SELECT IFNULL(SUM(trd_filled),0) FROM lbv.fundtrades WHERE trd_ticker='" + ticker + "'"
            shrsPrimus = float(mysql_conn.selectone(sql, 0))
            sql = "SELECT IFNULL(SUM(trd_filled),0) FROM lbv.ucitstrades WHERE trd_ticker='" + ticker + "'"
            shrsUcits = float(mysql_conn.selectone(sql, 0))
            shrsTotalBef = shrsPrimus + shrsUcits
            shrsTotalAft = shrsPrimus + shrsUcits + trades[ref]['shares'] + trades[ref+'|EQUUS']['shares']
            
            xrate = 1.0
            if trades[ref]['ccy'] != "EUR":
                sql = "SELECT ccy_xrate FROM lbv.histccy WHERE ccy_name='" + \
                        trades[ref]['ccy'] + "' AND ccy_date='2018-07-09'"
                        # trades[ref]['ccy'] + "' AND ccy_date='" + trades[ref]['date'] +"'"
                xrate = float(mysql_conn.selectone(sql, 0))
            
            mult = 0.01 if trades[ref]['ccy'] == "GBP" else 1
            
            amountPrimus = (shrsPrimus * trades[ref]['price'] * mult) / xrate
            amountUCITS = (shrsUcits * trades[ref]['price'] * mult) / xrate
            amountTotalBef = (shrsTotalBef * trades[ref]['price'] * mult) / xrate
            amountTotalAft = (shrsTotalAft * trades[ref]['price'] * mult) / xrate
            
            weightPrimus = amountPrimus / aumprimus
            weightUcits = amountUCITS / aumucits
            weightTotalBef = amountTotalBef / (aumprimus + aumucits)
            weightTotalAft = amountTotalAft / (aumprimus + aumucits)
            
            xPrimus = (weightTotalAft * aumprimus * xrate) / (trades[ref]['price'] * mult)
            xUcits = (weightTotalAft * aumucits * xrate) / (trades[ref]['price'] * mult)
            
            if (xPrimus - shrsPrimus) < trades[ref]['shares']:
                trades[ref]['shares'] += trades[ref+'|EQUUS']['shares']
            elif (xUcits - shrsUcits) < trades[ref+'|EQUUS']['shares']:
                trades[ref+'|EQUUS']['shares'] +=trades[ref]['shares']
            
            totalshares =  trades[ref]['shares'] + trades[ref+'|EQUUS']['shares']
            newsharesprimus = int(totalshares * (aumprimus / (aumprimus + aumucits)))
            newsharesucits = int(totalshares * (aumucits / (aumprimus + aumucits)))
            newsharesucits = newsharesucits + (totalshares - (newsharesprimus + newsharesucits))
            trades[ref]['shares'] = newsharesprimus
            trades[ref+'|EQUUS']['shares'] = newsharesucits
            
    #print json.dumps(trades, sort_keys=True, indent=4, default=json_serial)  
    
    r = {}
    for key in sorted(trades.iterkeys()):
        r[key] = trades[key]
    
    return r


