#!/usr/bin/env python
# coding: utf-8

# # lastの出力を読み込むファイル
# 
# v1.1
# 入力:
# - lastのdirを記述したtxtファイル...dirlistfile
# - dir内,lastの出力であるmyalns.maf

# In[1]:


import eval_fam_func as func

# In[6]:


truth_ref = func.get_truthref("truth_ref.txt")


# ## step6 アラインメント情報を取り込む
# 
# fam_coveredはdict型
# fam_covered\[truth\] = \[\[tstname,tstlength,truthreverse(±),tstreverse(±),truthbegin,truthcover,tstbegin,tstcover\]\]

# In[7]:


dirlist = func.get_dirlist("dirlist.txt")
fam,truth_length = func.get_last_out(dirlist)


# ## step7 可視化用辞書の作成
# 
# 
# {Repeat名:\[tst_repname,±,number_occ,-boundary,-not_covered,-covered,+covered,+not_covered,+boundary\]}

# In[10]:


vl = func.visualize_truth(fam,truth_length,truth_ref)
func.fprint_vl(vl)


# In[ ]:




