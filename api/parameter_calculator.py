'''
2025.1.6 created by Yada Honoka.(honoka_yada@icloud.com)
パラメータを計算しcsvファイルを出力するAPI
'''
import json 
import pandas as pd
import glob
from natsort import natsorted
from json2df import json_to_keypoint_df
from keypoint2parameter import cal_param
from flask import Blueprint, jsonify, request

# BluePrintの作成
parameter_calculator_bp=Blueprint('parameter_calculator_bp',__name__)

# # データとの紐付け
# data_name={
#     1:'Abe',
#     2:'Ehara',
#     3:'Koga',
#     4:'Kobayashi',
#     5:'Taketoshi',
#     6:'Noda',
#     7:'Hujiwara1',
#     8:'Hujiwara2',
#     9:'Miyashiro',
#     10:'Yamada',
#     11:'Ueda',
#     12:'kuwamoto'
# }

@parameter_calculator_bp('/data',methods=['GET'])
def parameter_calculator():
    pass
    # JSONファイルのパス
    json_dir=request.args.get('foldername')
    global FPS_data
    FPS_data=240
    json_df =[]


    print("JSONフォルダ内からJSONファイルを検索...")
    for jsonfile in natsorted(glob.glob(f"{json_dir}/*.json")):
        with open(jsonfile, 'r') as f:
            json_data= json.load(f)
            df_data=json_to_keypoint_df(json_data)
            json_df.append(df_data)




# if __name__=='__main__':

#     json_dir = '/Users/honoka/Desktop/研究/241115/support'
#     global FPS_data
#     FPS_data=240

#     json_df =[]

#     print("JSONフォルダ内からJSONファイルを検索...")
#     for json_file in natsorted(glob.glob(f"{json_dir}/**/*.json")):
#         with open(json_file, 'r') as f:
#             json_data=json.load(f)
#             df_data=json_to_keypoint_df(json_data)
#             json_df.append(df_data)
#     print('%d 個のJSONファイルを検出しました'%(len(json_df)))
#     print('JSONファイルをデータフレームに変換しました')

#     # 座標データのカラムとインデックスを入れ替えるリスト
#     point_data_df=[]
#     for df in json_df:
#         df=df.T
#         point_data_df.append(df)

#     with pd.ExcelWriter("support_original_data.xlsx") as writer:
#         for i in range(len(point_data_df)):
#             df=point_data_df[i]
#             df.to_excel(writer,sheet_name=data_name[i+1])
#             print('%d 人目の座標データをExcelファイルに保存しました'% (i+1))


#     # パラメーターを計算後のデータを格納するリスト
#     param_df = []
#     print("座標データからパラメータを計算します")
#     for df in json_df:
#         cal_df=cal_param(df,FPS_data)
#         param_df.append(cal_df)
#         print('%d 人目のパラメータの計算が完了しました'% (len(param_df)))

#     with pd.ExcelWriter("v4_support_param.xlsx") as writer:
#         for i in range(len(param_df)):
#             df=param_df[i]
#             df.to_excel(writer,sheet_name=data_name[i+1])
#             print('%d 人目のパラメータデータをExcelファイルに保存しました'% (i+1))



