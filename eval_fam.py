# # familyの重なり方を評価するプログラム
# 
# ## 入力
# - 正解のRepeatMasker out file
# - out.reprofに対するRepeatMasker out file
# <br>
# - 正解のライブラリ
# - out.reprof
# 
# ## 出力
# repeatの名前,class,出現回数,consensusの長さ,mapされているtestのrepeatの名前
# をまとめたファイル

import argparse

import eval_fam_func as func


# ## step1 RepeatMasker out fileを得る
# 
# 正解のRepeatMasker out fileを入力し,加工して行列にする<br>
# \[name, class, start, end\]<br>
# とする.<br>
# <br>
# テストの行列は、<br>
# \[name, class(unknown), start, end, frag\]<br>
# とする

parser = argparse.ArgumentParser(description='repeatmaskerの.outの重なり方を比較し,LASTにかける用の配列を生成する')

parser.add_argument('tstout', help='repeatmmaskerの.outファイル,tst')    # 必須の引数を追加
parser.add_argument('truthout', help='repeatmmaskerの.outファイル,truth')
parser.add_argument('tstreprof',help='out.reprofファイル,tst')    # オプション引数（指定しなくても良い引数）を追加
parser.add_argument('truthreprof', help='out.reprofファイル,truth')   # よく使う引数なら省略形があると使う時に便利

args = parser.parse_args()    # 4. 引数を解析


tstname = args.tstout
truthname = args.truthout


tst_out = func.read_repeatmasker_out(tstname,None,1)
truth = func.read_repeatmasker_out(truthname)


# ## step2 重なっているRepeatを抜き出す
# 
# 出力系は<br>
# fam...dict(truthのrepeat番号)\[tstのrepeat番号,出現回数\]
# truthref...\[truthのrepeat番号,class,出現回数 \]のlist
# - tstから一回も出現しなかったrepeatの出力
# - truthにおいて一回も重ならなかったrepeatの出力



replist,repref,nonappeartst,nonappeartruth=func.repeatcheck(truth,tst_out)


func.nonappearout(nonappeartst,"tst_non")
func.nonappearout(nonappeartruth,"truth_non")
func.truthrefout(repref)


# ## step3 fastaファイルを作成

# dirを作成
# lastをかけられる状態にする


tstlib = args.tstreprof
truthlib = args.truthreprof

func.tstout_compare(tst_out,tstlib)


func.makelastdir(replist,truthlib,tstlib)

