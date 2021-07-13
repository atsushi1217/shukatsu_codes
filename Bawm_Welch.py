import numpy as np
import os
import argparse

import seqgen
import posterior_decoding as pd
import Viterbi

parser = argparse.ArgumentParser(description='長さLの配列に対してBaum_Welchを実行、VIterbiと事後デコーディングで評価')

parser.add_argument('-L','--L', help='配列長を指定',type = int ,default=30000)   

args = parser.parse_args()

L = args.L
y,x = seqgen.seqgen(L)

# 出力確率Eの初期値,及び遷移確率Aの定義
E = np.array(([5/20,3/20,2/20,8/20,1/20,1/20],[1/20,2/20,3/20,8/20,1/20,5/20]))
A = np.array(([0.5,0.5],[0.5,0.5]))
K = 2 #隠れ状態


# Eステップ
def Forward_scale(Dice_emit,A,x):
    X = len(x)
    f_wave = np.zeros((K,X+1)) #スケーリングされたforward変数fを格納する行列
    s = np.zeros((X+1)) #スケーリング変数sの初期化
    f_wave[:,0] = 0.5
    s[0] = 1
    for i in range (1,X+1):
        a = int(x[i-1])-1 #出目の管理
        sumup = np.zeros((K)) #f_wave,及びs計算用に用いられるシグマ計算用
        for l in range(K):#スケーリング変数sの更新用ループ
            for k in range(K):
                sumup[l] = f_wave[k,i-1] * A[k,l] + sumup[l]
            s[i] = Dice_emit[l,a] * sumup[l] + s[i]
        for l in range(K):#f_wave更新用ループ
            f_wave[l,i] = Dice_emit[l,a] * sumup[l] / s[i]

    return f_wave,s

def backward_scaling(Dice_emit,A,x,s):
    X = len(x)
    B = np.full((K,X),0.0)
    B[:,X-1] = [1.0,1.0]
    for i in reversed(range (1,X)):
        backemit = np.zeros(K)#scaling中身の計算用
        a = int(x[i])-1 #出目の管理
        for k in range(K):
            for l in range(K):
                backemit[k] = A[k,l] * Dice_emit[l,a] * B[l,i]  + backemit[k]

        for k in range(K):
            B[k,i-1] = backemit[k]/s[i+1] 
         
    return B

def Estep(x,K,E,A):#入力配列,隠れ状態数,出力確率,遷移確率
    X = len(x)
    E_update = np.zeros((K,6))
    A_update = np.zeros((K,K))
    forward,s1 = Forward_scale(E,A,x)
    backward = backward_scaling(E,A,x,s1)
    # Eの更新
    for k in range(K):
        for b in range(6):
            xi = b+1
            for i in range(X):
                if x[i] == str(xi):
                    E_update[k,b] = E_update[k,b] + forward[k,i+1]*backward[k,i] #forwardの列数が一つずれているので注意
    # Aの更新
    for l in range(K):
        for k in range(K):
            for i in range(X-1):
                deme = int(x[i+1])-1
                A_update[k,l] = A_update[k,l]+forward[k,i+1]*A[k,l]*E[l,deme]*backward[l,i+1]/s1[i+2]#sの列数も一つずれているので注意
    
    return E_update,A_update,s1


# Mステップ


def Mstep(E_update,A_update,K):
    NA = np.zeros((K,K))
    NE = np.zeros((K,6))
    #newA
    for k in range(K):
        Asum = 0
        for l in range(K):
            Asum = Asum + A_update[k,l]
        for l in range(K):
            NA[k,l] = A_update[k,l]/Asum
    #newE
    for k in range(K):
        Esum = 0
        for b in range(6):
            Esum = Esum + E_update[k,b]
        for b in range(6):
            NE[k,b] = E_update[k,b]/Esum
    
    return NE,NA



def LLH(x,s,s_old):#loglikelyhoodを計算
    flag = 1
    X = len(x)
    s_new = np.log(1)
    for i in range(1,X+1):
        s_new = s_new + np.log(s[i])

    scompare = s_new - s_old
    if scompare < 0.01:
        flag = 0

    return flag,s_new

def eval_seq(L,y,V,D):#(長さ,正解データ,Viterbiデータ,PDデータ)
    Vcount = 0 #Viterbi正解数のカウント
    Dcount = 0 #PD正解数のカウント
    for i in range(L):
        if y[i] == V[i]:
            Vcount = Vcount + 1
        if y[i] == D[i]:
            Dcount = Dcount + 1
    Vp = Vcount/L
    Dp = Dcount/L
    
    return Vp,Dp


flag = 1
j = 0
s_new = -float('inf')
while(flag  == 1):
    s_old = s_new
    E_update,A_update,s = Estep(x,K,E,A)
    E,A = Mstep(E_update,A_update,K)
    flag,s_new = LLH(x,s,s_old)
    j += 1
    
    print("%d回目のループ"%j)
    print("E = ",E)
    print("A = ",A)


# In[9]:
print('ループ回数は:',j)
print('推定された遷移確率は\n',A)
print('推定された出力確率は\n',E)


lgE = np.log(E)
lgA = np.log(A)

correct = np.zeros((2,1))

#Viterbiで解く
V =Viterbi.Viterbi(x,lgE,lgA,Viterbi.FLemit)
# 事後デーコーディングで解く
F,s1 = pd.Forward_scale(E,A,x)
B,s2 = pd.backward_scaling(E,A,x)
D = pd.decording(F,B,x)
#正解率計算
correct = eval_seq(L,y,V,D)
print('（Viterbiの正解率,PDの正解率）')
print(correct)