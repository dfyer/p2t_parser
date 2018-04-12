# -*- coding: utf-8 -*-

#import xml.etree.ElementTree as ET
##import xml.etree.ElementTree.XMLParser as XMLParser
#from xml.etree.ElementTree import XMLParser
from lxml import etree
from bs4 import BeautifulSoup
import pprint as pp
import re
import sys
import os
import codecs
import datetime

delimiter = "$"

def pdftotxt(path, inputpdf, outputfile):
    ret_list = []

    file_name=inputpdf[:-4]
    target_pdf = path + inputpdf
    target_pdf = target_pdf.replace(" ", "\ ")
    target_pdf = target_pdf.replace("(", "\(")
    target_pdf = target_pdf.replace(")", "\)")
    #print("pdftohtml -enc UTF-8 -xml " + target_pdf + " buffer")
    os.system("pdftohtml -enc UTF-8 -xml " + target_pdf + " buffer")

    #file_name=inputfile[10:-4]

    metadata = ["", "", "", "", ""]
    #region,conference_type,date,number,cha='','','','',''
    #print(file_name)
    #print(file_name.split('_'))
    if len(file_name.split('_')) >= 5:
        metadata = file_name.split('_')[:5]
    else:
        for i in range(len(file_name.split('_'))):
            metadata[i] = file_name.split('_')[i]
    [region,conference_type,date,number,cha] = metadata
    if region=='울산':
        region='울산시'
    region=region.decode('utf-8')
    conference_type=conference_type.decode('utf-8')
    date=date.decode('utf-8')
    number=number.decode('utf-8')
    cha=cha.decode('utf-8')

    # Strip span
    soup = BeautifulSoup(open("buffer.xml"), 'lxml')
    [s.unwrap() for s in soup.findAll('span')]
    with open("buffer.clean.xml", "w") as f:
        f.write(str(soup))

    #tree = ET.parse(inputfile)
    #parser = XMLParser(recover=True)
    #tree = ET.parse("buffer.xml", parser)
    parser = etree.XMLParser(recover=True)
    tree = etree.parse("buffer.clean.xml", parser)
    root = tree.getroot()


    if outputfile != "":
        f=codecs.open(outputfile,'a','utf-8')

    diff_list=[]

    page=""
    item=""

    title=""

    p_end=re.compile(u'산회\)')
    p_end2=re.compile(u'폐식\)')
    p_end3=re.compile(u'감사종료\)')
    p_commentor=re.compile(u'^[^ $]+ +[^ $]+')
    p_uiwon=re.compile(u'^[^ $]+의원')
    p_wiwon=re.compile(u'^[^ $]+위원')
    p_noname=re.compile(u'^[$]')
    #p_uiwon=re.compile(u'^[^ ]+의[ \t]*원')

    end_minutes = False
    mul_item = True


    ################################### extracting text
    for page_it in root.iter("page"):
        first_line = True
        if end_minutes:
            break
        for text_it in page_it.iter("text"):
            if first_line == True:# skip the first line of each page since it is date info
                first_line = False
                continue
            text=text_it.text
            if not text:
                continue
            if p_end.search(text) or p_end2.search(text) or p_end3.search(text):
                end_minutes = True
                break
            page=page+text+delimiter

            #print text

    #print page

    ##################################### comment parsing

    page_end=False
    num=0
    msg=""
    ret=""
    str_item=""
    # Original
    target_symbol=u'○'
    # Dongjak, Seoul
    #target_symbol=u'◇'
    # Gwangsan-gu, Gwangju
    #target_symbol=u'o'
    # Gunsan-si
    #target_symbol=u'○'
    # Chulwon-gun
    #target_symbol=u'◎'
    end_symbol=u'─────'
    end_symbol2=u'------'
    count=0

    appendix_symbol=u'\u3010\ucc38\uc870\u3011'
    last_idx=page.find(appendix_symbol)
    if last_idx != -1:
        page=page[:last_idx]

    while page_end==False:
        sym=page.find(target_symbol,num+1)
        num=sym
        sym2=page.find(target_symbol,sym+1)
        if sym2==-1:
            page_end=True
        raw_msg=page[sym+1:sym2].replace(u"     ", " ")
        #print(raw_msg)
        #print(page)
        raw_msg=raw_msg.replace(u" ", " ")
        raw_msg=raw_msg.replace(u"   ", " ")
        raw_msg=raw_msg.replace(u" ", " ")
        raw_msg=raw_msg.replace(u" ", " ")
        raw_msg=raw_msg.replace(u" ", " ")
        raw_msg=raw_msg.replace(u"·", "")
        raw_msg=raw_msg.replace(u" ", " ")
        raw_msg=raw_msg.replace(u":", " ")
        raw_msg=raw_msg.strip()
        # Asan-si
        #raw_msg=raw_msg.split(u"-")[0]
        #raw_msg=raw_msg.split(u"─")[0]
        # Gunpo-si
        #raw_msg=raw_msg.replace(u"「$」", "")
        #raw_msg=raw_msg.replace(u"「 」", "")
        #raw_msg=raw_msg.replace(u"ｏ", "")
        # Gwacheon-si
        #raw_msg=raw_msg.split(u"Page")[0]
        # Osan-si
        #raw_msg=raw_msg.replace(u"    ", " ")
        #raw_msg=raw_msg.replace(u" ", " ")
        #raw_msg=raw_msg.replace(u" ", " ")
        #raw_msg=raw_msg.split(u"페이지")[0]
        # Seocheon-gun
        #raw_msg="$".join(raw_msg.split("$")[:-5])
        # Gwangju-si
        #raw_msg=raw_msg.replace(u" ", " ")
        #raw_msg=raw_msg.replace(u"   ", " ")

        #print(raw_msg)

        ## Remove Footnote
        #position = -1
        #before = 1
        #after = 1
        #for i, line in enumerate(raw_msg.split("$")):
        #    if line.startswith("http"):
        #        position = i
        #if position > 0:
        #    raw_msg="$".join( raw_msg.split("$")[:position-before] + raw_msg.split("$")[position+1+after:] )

        #print(raw_msg)
        #assert False
        try:
            if len(p_uiwon.findall(raw_msg)) is not 0:
                #print("A")
                commentor=p_uiwon.findall(raw_msg)[0]
                msg=p_uiwon.split(raw_msg,1)[1].replace("$", "")
            elif len(p_wiwon.findall(raw_msg)) is not 0:
                #print("B")
                commentor=p_wiwon.findall(raw_msg)[0]
                msg=p_uiwon.split(raw_msg,1)[1].replace("$", "")
            elif len(p_noname.findall(raw_msg)) is not 0:
                #print("C")
                commentor=""
                msg=p_noname.split(raw_msg,1)[1].replace("$", "")
            else:
                #print("D")
                commentor=p_commentor.findall(raw_msg)[0]
                # Osan-si
                if len(commentor.split(u"참석자")) > 1:
                    continue
                msg=p_commentor.split(raw_msg,1)[1].replace("$", "")
            # Gunsan-si
            #if len(raw_msg.split("$")) > 2:
            #    commentor = raw_msg.split("$")[0]
            #    msg="".join(raw_msg.split("$")[1:])
            #else:
            #    continue
        except:
            #print(sys.exc_info())
            print("Failed retrieving msg")
            continue

        if len(msg) is 0:
            #print 'empty msg'
            continue


        #print commentor
        #print msg

        msg=msg.replace("  "," ")
        #print '!'+commentor,
        #print '!'+msg
        #assert False

        count=count+1
        spk_num=str(count).decode('utf-8')
        #ret=region+','+date+','+conference_type+','+number+',"'+cha+'","'+commentor+'",'+spk_num+',"'+msg+'",'+inputfile.decode('utf-8')+'\n'
        ret=region+','+date+','+conference_type+','+number+',"'+cha+'","'+commentor+'",'+spk_num+',"'+msg+'"\n'
        #print(ret)
        if outputfile != "":
            f.writelines(ret)
        ret_list.append(ret)

    return ret_list


def main():
    start_time = datetime.datetime.now()
    #inputfile="src/ulsan/xml/øÔªÍ_¿«»∏øÓøµ¿ßø¯»∏_2014717_163_1.xml"
    #outputfile="tmp.csv"
    """
    paths = ["군산시/", "김제시/", "부안군/", "순창군/", "전주시/", "정읍시/", "서산시/", "서천군/", "아산시/", "가평군/",
            "고양시/", "과천시/", "광주시/", "구리시/", "군포시/", "김포시/", "남양주시/", "부천시/", "수원시/",
            "안성시/", "양평군/", "오산시/", "용인시/", "의정부시/", "이천시/", "평택시/", "광양시/", "무안군/",
            "순천시/", "영광군/", "영암군/", "완도군/", "장흥군/", "함평군/", "해남군/", "화순군/",
            "고창군/", "남원시/", "무주군/", "완주군/", "익산시/", "임실군/", "장수군/", "진안군/"]
    """
    #paths = ["세종시", "여주시", "의정부시", "평택시"]
    #paths = ["강릉시", "삼척시", "태백시", "정선군", "고성군",
    #         "양양군", "횡성군", "영월군", "양구군"]
    #paths = ["광주광산구", "대전유성구", "부산진구", "부산동래구", "부산남구",
    #         "부산해운대구", "부산기장군", "부산사하구",
    #paths = ["울산중구", "울산남구", "울산동구", "울산북구", "울산울주군"]
    #paths = ["창원시", "진주시", "통영시", "경남고성군", "사천시",
    #         "김해시", "밀양시", "거제시", "의령군", "함안군",
    #         "창녕군", "양산시", "하동군", "남해군", "함양군",
    #         "산청군"]
    #paths = ["포항시", "경주시", "김천시", "안동시", "구미시",
    #         "영주시", "영천시", "예천군", "청도군", "고령군",
    #         "성주군", "칠곡군", "군위군", "영양군", "봉화군",
    #         "울진군",
    #         "도봉구", "노원구", "서대문구", "마포구", "양천구",
    #         "강서구", "구로구", "중구", "동작구", "관악구",
    #         "서초구", "강동구", "용산구", "성동구", "광진구",
    #         "동대문구", "성북구", "강북구"]
    #paths = ["광주광산구"]
    #paths = ["정선군"]
    #paths = ["춘천시", "원주시", "화천군", "철원군", "화성시",
    #         "시흥시", "울릉군"]
    #paths = ["속초시", "거창군", "상주시", "의성군", "청송군",
    #         "영등포구", "송파구"]
    paths = ["금천구"]
    paths = map(lambda x: x+"/", paths)
    for path in paths:
        outputfile=""#"Asdf"
        all_list = []
        count = 0
        read = 0
        valid = 0
        err_list = []
        for i, inputpdf in enumerate(os.listdir(path)):
            if inputpdf.endswith(".pdf"):
                #print(str(path+inputpdf).decode('utf-8'))
                #skip = 0
                #if i > skip:
                #    break
                #if i < skip:
                #    continue
                count += 1
                try:
                    read += 1
                    out_list = pdftotxt(path, inputpdf, outputfile)
                    if out_list:
                        valid += 1
                    all_list.extend(out_list)
                    print(datetime.datetime.now())
                except:
                    print(sys.exc_info())
                    err_list.append(str(path+inputpdf).decode('utf-8') + "|" + str(sys.exc_info()))
        #print("".join(all_list).encode("utf-8"))
        with open(path.split("/")[0] + ".out.csv", "w") as f:
            f.write("".join(all_list).encode("utf-8"))
        summary = str(count) + " files, " + str(read) + " read, " + str(valid) + " valid."
        print(summary)
        with open(path.split("/")[0] + ".err.txt", "w") as f:
            f.write(summary + "\n")
            f.write("\n".join(err_list).encode("utf-8"))

    print("Started at:")
    print(start_time)
    print("Ended at:")
    print(datetime.datetime.now())


if __name__=="__main__":
    main()
