import re
import cefpyco
import time
import random
import subprocess
import sys




# Network Function Name
shareContentnum=int(sys.argv[1])
id="2"
mycontentsnum=int(id)-1
functionName = "/preInterest"
nodeinfo="/node"+id
contentsnamearr=[]
mysequence=[]
kihonn="Temp"
mycontentsname= "Temp" + id
mode=0#コンテンツを所持していないルータ
if int(id) <= shareContentnum:
    mode = 1#コンテンツを所持しているルータ

print("my mode=" +str(mode))
print("share contents num:" + str(shareContentnum))


for i in range(shareContentnum):
    CN=kihonn+str(i+1)
    contentsnamearr.append(CN)
    mysequence.append(0)



pushChunkNum = 3
preInterestRecvNum=0
rejectedpreNum=0
InterestRecvNum=0
DataRecvNum=0
sendI=0
sendD=0
sendpreI=0
sequence=0
endI=60
count=0
filename="result"+ id + ".txt"
f=open(filename, "w")
updatenum=100
updateI=60
lamba=1/updateI

start_time=time.time()
n=10.0+(mycontentsnum*10) #5秒後に更新するために利用
temp = 20
"""
args=sys.argv
if len(args)==0:
    print("I can't do Flooding")
    exit()

f=open(args[0], 'r')
datalist = f.readlines()
"""
#最初にFIBに接続しているノードの情報を取ってくる
def facenum_FIB(contentsname):#FIBの中からFace番号を読み取る
    searchnum='cefstatus | grep -A 1 \"' + contentsname + '\" | grep \"Faces\"'
    proc = subprocess.run(searchnum, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    facenum=re.findall(".*?(\d+).*?", proc.stdout.decode('cp932'))
    return facenum#Face番号の配列を返す

def faceid_FIB(facenum):#FIBの中からfacenumに対応したaddressを返す
    searchaddress='cefstatus | grep \"faceid\" | grep \" ' + facenum + ' \"'
    proc = subprocess.run(searchaddress, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    faceadd=re.findall(".*?(\d+.\d+.\d+.\d+):.*?", proc.stdout.decode('cp932'))
    print("faceadd:" + str(faceadd))
    return faceadd[0]#対応したaddressを返す

def end_check(mysequence, updatenum, shareContentnum):
    flag=1
    for i in range(shareContentnum):
        if mysequence[i]!=updatenum:
            flag=0
    return flag
    





def time_cal():#時間計測を行うための関数
    now_time=time.time()
    elapsed_time=now_time -start_time
    return elapsed_time

def thermometer():
    tmr = random.randint(10, 25)
    print("Update Data! Now temperture is " + str(tmr))
    return tmr

def facenum_pit(preinterestname):
    searchnum = 'cefstatus --pit'
    proc = subprocess.run(searchnum, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(proc.stdout.decode('cp932'))
    facenum=re.findall(preinterestname + "(?:.|\s)*?Chunk=\d+(?:.|\s)*?" + ".*?(\d+)" , proc.stdout.decode('cp932'))
    #print(facenum)
    #facenum=re.findall(".*?(\d+).*?",proc.stdout.decode('cp932'))
    return facenum[0]#文字列形式で返す

def facenum_tosendI(preinterestname):#送信されてきたpreInterestがどのFace番号化を読み取る
    #searchnum ='cefstatus | grep -A 1 \"' + preinterestname + "\" | grep \"Faces\""
    searchnum = 'cefstatus'
    proc = subprocess.run(searchnum, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    facenum=re.findall(preinterestname + "(?:.|\s)*?Chunk=\d+(?:.|\s)*?" + ".*?(\d+)" , proc.stdout.decode('cp932'))
    #print(facenum)
    #facenum=re.findall(".*?(\d+).*?",proc.stdout.decode('cp932'))
    return facenum[0]#文字列形式で返す


def FIBregist(preI, Interestpre, facenum, faceadd):#preInterestnameからFace番号を読み取り、そのFace番号にコンテンツがあると仮定してFIBに追加する
    nowface=facenum_tosendI(preI)
    for i in range(len(facenum)):
        if nowface==facenum[i]:#preInterest送信元に対するInterestのFIBを追加
            addroute='sudo cefroute add ' + Interestpre + ' udp ' + faceadd[i]
            proc = subprocess.run(addroute, shell=True)
            #print("Add route " + Interestpre + " Face: " + facenum[i])
        else:#Interest送信元以外に対するpre Interest転送用のFace番号の追加
            addroute= 'sudo cefroute add ' + preI + ' udp ' + faceadd[i]
            proc = subprocess.run(addroute, shell=True)
            #print("Add route " + preI + " Face: " + facenum[i])

def FIBderegist(FIBname, faceadd):
    for i in range(len(faceadd)):
        delroute='sudo cefroute del ' + FIBname + ' udp ' + faceadd[i]
        proc = subprocess.run(delroute, shell=True)
        #print("Del route " + FIBname + " Face:" + facenum[i])

def FIBregistall(FIBname, faceadd):
    for i in range(len(faceadd)):
        addroute= 'sudo cefroute add ' + FIBname + ' udp ' + faceadd[i]
        proc = subprocess.run(addroute, shell=True)
        #print("Add route " + preI + " Face: " + facenum[i])



def interest_history(interestname):#そのinterestが既にFIBに登録されているかどうかを判別
    search = 'cefstatus | grep -A 1 \"' + interestname + "\" | grep \"Faces\""
    proc = subprocess.run(search, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if (proc.stdout.decode('cp932')==""):#既にFIBに登録済みであった場合
        flag=1
    else:#登録を行っていなかった場合
        flag=0
    return flag#interestを送信済みの場合は1を、まだinterestを返していない場合は0を返す

def packethistory():
    print("pre Interest Num:"+ str(preInterestRecvNum))
    print("pre Interest Rejected Num:"+ str(rejectedpreNum))
    print("Interest Num:"+str(InterestRecvNum))
    print("Data Num:"+str(DataRecvNum))
    print("Send Data Num:" + str(sendD))
    print("Send Interest Num" + str(sendI))
    print("Send preI Num" + str(sendpreI))

interestNamePrefix= "ccnx:" + functionName #ccnx:/Flooding
#FIBから接続しているノードのFace番号とIPaddressを取得
facenum=facenum_FIB(interestNamePrefix)
faceadd=[]
print(facenum)


for i in range(len(facenum)):
    print(facenum[i])
    faceadd.append(faceid_FIB(facenum[i]))
    print("facenum:" + facenum[i] + "faceaddress: " + faceadd[i])



#FIBderegist(interestNamePrefix, faceadd)

faces=len(facenum)


with cefpyco.create_handle() as handle:
    Name_pushData="ccnx:" +  "/" + mycontentsname#ccnx:/Temp1
    if mode == 1:
        preInterestName="ccnx:" + functionName +  "/" + mycontentsname + "/" + str(mysequence[mycontentsnum]) + "/" + str(pushChunkNum) #ccnx:/Flooding/chunknum/Temp/mysequence
    

    handle.register(interestNamePrefix)#ccnx:/Floodingからpre Interestを受信する用意
    handle.register(Name_pushData)#ccnx:/contentsnameからInterestを受信する用意
    
    def start_flooding(filename):
        print("Start Flooding! File name is" + filename)
        print("Send an pre Interest with a name:" + preInterestName)
        handle.send_interest(preInterestName, 0)#ccnx:/Flooding/chunknum/node1/mysequence/nodeinfoというpre Interestを送信


    """
    def File_search(sender_name, sender_sequence, interestname, nodeinfo):#fileが存在するかどうか
        for i in range(len(filename)):
            if filename[i]==sender_name:#既に受け取っているファイルであったら
                if sequence[i]<sender_sequence:#シーケンス番号が新しいものであったら
                    DataRecvNum[i]=0#受信したDataパケットの数を0にしておく
                    return 1
                else:
                    print("It is old file!")
                    return 0
            else:
                print("This is a file I haven't received yet")
                filename.append(sender_name)
                sequence.append(sender_sequence)
                cefrouteadd(interestname, nodeinfo)#interestを送信するようのPITを準備
                return 1
    """
    """
    def filenum_search(contentsname, contents_sequence):
        for i in range(len(filename)):
            if filename[i]==contentsname:#filename配列とコンテンツ配列が一致
                if sequence[i]==contents_sequence:#シーケンス番号と新規コンテンツのシーケンス番号が一致
                    handle.send_data()
    """
    

    while True:
        #更新が起きたらpre Interest Floodingの開始
        elapsed_time=time_cal()
        #packethistory()
        if mode == 1:#コンテンツ所持者
            if(elapsed_time >= n and mysequence[mycontentsnum]<updatenum):#更新が起きたら
                mysequence[mycontentsnum]+=1
                #nowtime=time.time()
                #f.write("sequence:" + str(mysequence[0]) + " time:" +str(nowtime) + "\n")#時間計測用
                temp=thermometer()
                print("My sequence is " + str(mysequence[mycontentsnum]))
                rand_Time=random.expovariate(lamba)
                n = elapsed_time + rand_Time
                #preInterestName="ccnx:" + functionName + "/" + str(pushChunkNum) + "/" +mycontentsname + "/" + str(mysequence[mycontentsnum]) #ccnx:/network/Flooding/chunknum/Temp/mysequence
                preInterestName="ccnx:" + functionName  + "/" + mycontentsname + "/" + str(mysequence[mycontentsnum]) + "/" + str(pushChunkNum)
                print("Send an pre Interest with a name:" + preInterestName)
                FIBregistall(interestNamePrefix, faceadd)
                handle.deregister(interestNamePrefix)#regist済みの場合そちらが優先されてしまうccnx:/Floodingの消去
                handle.send_interest(preInterestName, 0) #ccnx:/network/Flooding/chunknum/node1/mysequence(Floodingの開始)
                handle.register(interestNamePrefix)#再度regist(ccnx:/Flooding)
                FIBderegist(interestNamePrefix, faceadd)
                sendpreI+=faces
                
        
            if(mysequence[mycontentsnum]>=updatenum):
                nowtime=time.time()
                if count==0:
                    endT=nowtime+endI
                    count+=1
                elif endT<nowtime:
                    print("Finish!! sequence arrive in " + str(sequence))#sequence番号が10になったら終了
                    f.close()
                    print("Finish!! sequence arrive in " + str(sequence))#sequence番号が10になったら終了
                    sys.stdout = open(filename, 'a')
                    packethistory()
                    sys.stdout = sys.__stdout__
                    break
        
        else:
            if(mysequence[shareContentnum-1]>=updatenum):
                flag=1
                for i in range(shareContentnum):
                    if mysequence[i]!=updatenum:
                        flag=0
                if flag ==1:
                    nowtime=time.time()
                    if count==0:
                        endT=nowtime+endI
                        count+=1
                    elif endT<nowtime:
                        print("Finish!! sequence arrive in " + str(sequence))#sequence番号が10になったら終了
                        f.close()
                        print("Finish!! sequence arrive in " + str(sequence))#sequence番号が10になったら終了
                        sys.stdout = open(filename, 'a')
                        packethistory()
                        sys.stdout = sys.__stdout__
                        break

        
        #packetの受信
        info = handle.receive()#packetを受信
        if info.is_succeeded: #packetの受信が成功した場合
            if info.is_interest: #受信したパケットがInterestパケットだった場合
                if interestNamePrefix in info.name:#pre Interestパケットだった場合
                    preInterestRecvNum+=1
                    #自分以外がFloodingしたpre Interestパケットだった場合
                    print("Receive pre Interest: {}".format(info))
                    #chunkNum = re.findall(interestNamePrefix + "/(.*?)/", info.name)#chunkNum[0]=/sender_chunksize
                    #sender_name = re.findall(interestNamePrefix + "/.*?/(.*)/.*?", info.name)#namePrefix[0]=contents_name
                    sender_name = re.findall(interestNamePrefix + "/(.*?)/", info.name)
                    sender_sequence = re.findall(interestNamePrefix + "/.*?/(.*)/.*?", info.name)#sequence[0]=sender_sequence
                    chunkNum = re.findall(interestNamePrefix + "/.*?/.*?/(.*)", info.name)
                    interestName = "ccnx:/" + sender_name[0] + "/" + sender_sequence[0]#ccnx:/sender_nodeinfo/sender_sequence
                    returnflag=0
                    for i in range(int(chunkNum[0])):
                        if contentsnamearr[i] == sender_name[0]:
                            if mysequence[i] < int(sender_sequence[0]):
                                nowcontentsnum=i
                                returnflag=1
                    
                    if returnflag==1:
                        #handle.deregister(interestpre)
                        interestName = "ccnx:/" + sender_name[0] + "/" + sender_sequence[0]#ccnx:/sender_nodeinfo/sender_sequence
                        searchnum = 'cefstatus'
                        #proc = subprocess.run(searchnum, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        #print(proc)
                        #FIBregist(info.name, interestName, facenum, faceadd)#新しいコンテンツに対応するFIBを登録
                        #Interest packets の送信
                        #dataRecvNum = 0
                        mysequence[nowcontentsnum]=int(sender_sequence[0])
                        for i in range(int(chunkNum[0])):
                            print("Send Interest: name: " + interestName + " chunk=" + str(i))#ccnx:/source
                            handle.send_interest(interestName, i)
                            sendI+=1
                        #handle.register(interestpre)
                        #pre Interestの転送
                        #handle.register(interestName)#ccnx:/contentsnameからInterestを受信する用意
                        #FIBderegist(interestName, faceadd)
                        #handle.deregister(interestNamePrefix)#ccnx:/FloodingをFIB(APP)から削除
                        #handle.send_interest(info.name, int(id))
                        #handle.register(interestNamePrefix)#ccnx:/FloodingをFIB(APP)に追加
                        #FIBderegist(info.name, faceadd)
                        #sendpreI += (faces - 1)
                        #print("Send pre Interest name with:" + info.name)
                    
                    else:
                        rejectedpreNum +=1

                if mode==1:
                    if (info.name == ("ccnx:/" + mycontentsname + "/" + str(mysequence[mycontentsnum]))):#自分が転送したpre interstに対するInterestパケットの場合
                        print("Recv Interest: {}".format(info))
                        msg = "Current-Temp: " +str(temp) +" degree celsius, chunk=" + str(info.chunk_num) + "\n"
                        InterestRecvNum += 1
                        print("Send Data: " + info.name + " chunk_num=" + str(info.chunk_num))
                        handle.send_data(info.name, msg, info.chunk_num, expiry=3600000, cache_time=360000) 
                        sendD+=1
					    #handle.send_data(info.name, msg, info.chunk_num)
                
                    

            elif info.is_data: #受信したパケットがDataパケットだった場合
                #data受信履歴の作成
                DataRecvNum+=1
                print(info)
                nowtime=time.time()
                f.write(str(nowtime)+"\n")

