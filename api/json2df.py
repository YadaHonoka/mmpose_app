'''
2025.01.06 YadaHonoka
jsonファイルのデータから、座標情報を取り出しDataFrameに変換し、返す関数
'''
import pandas as pd
import numpy as np

# jsonファイルをdfにする
# MMPoseが出力するJSONファイルのキーポイント座標のみをpandasのDataFrameへ変換する関数
def json_to_keypoint_df(results_data):
    num_frame=np.arange(len(results_data['instance_info']))
    keypoint_max=23 # キーポイントの最大値
    keypoint_list=[] # 16個のキーポイントをまとめるためのリスト
    nose = [] # "0": "nose"
    left_eye = [] # "1": "left_eye"
    right_eye = [] # "2": "right_eye"
    left_ear = [] # "3": "left_ear"
    right_ear = [] # "4": "right_ear"
    left_shoulder = []# "5": "left_shoulder"
    right_shoulder = []# "6": "right_shoulder"
    left_elbow = []# "7": "left_elbow"
    right_elbow = []# "8": "right_elbow"
    left_wrist = []# "9": "left_wrist"
    right_wrist = []# "10": "right_wrist"
    left_hip = [] # "11": "left_hip"
    right_hip = [] # "12": "right_hip"
    left_knee = [] # "13": "left_knee"
    right_knee = [] # "14": "right_knee"
    left_ankle = [] # "15": "left_ankle"
    right_ankle = [] # "16": "right_ankle"
    left_big_toe = [] # "17": "left_big_toe" 足の親指
    left_small_toe = [] # "18": "left_small_toe"
    left_heel = [] # "19": "left_heel"
    right_big_toe = [] # "20": "right_big_toe"
    right_small_toe = [] # "21": "right_small_toe"
    right_heel = [] # "22": "right_heel"

    for i in range(len(num_frame)):
        for n in range(keypoint_max):# JSONファイルからデータを取り出している
            x=results_data['instance_info'][i]['instances'][0]['keypoints'][n][0]
            y=results_data['instance_info'][i]['instances'][0]['keypoints'][n][1]

            # nはキーポイントの座標の番号(1はright_hip)
            if n==0:
                nose.append([x,y])
            if n==1:
                left_eye.append([x,y])
            if n==2:
                right_eye.append([x,y])
            if n==3:
                left_ear.append([x,y])
            if n==4:
                right_ear.append([x,y])
            if n==5:
                left_shoulder.append([x,y])
            if n==6:
                right_shoulder.append([x,y])
            if n==7:
                left_elbow.append([x,y])
            if n==8:
                right_elbow.append([x,y])
            if n==9:
                left_wrist.append([x,y])
            if n==10:
                right_wrist.append([x,y])
            if n==11:
                left_hip.append([x,y])
            if n==12:
                right_hip.append([x,y])
            if n==13:
                left_knee.append([x,y])
            if n==14:
                right_knee.append([x,y])
            if n==15:
                left_ankle.append([x,y])
            if n==16:
                right_ankle.append([x,y])
            if n==17:
                left_big_toe.append([x,y])
            if n==18:
                left_small_toe.append([x,y])
            if n==19:
                left_heel.append([x,y])
            if n==20:
                right_big_toe.append([x,y])
            if n==21:
                right_small_toe.append([x,y])
            if n==22:
                right_heel.append([x,y])

    # キーポイントをすべてのリストへ格納する
    keypoint_list = [nose,left_eye,right_eye,left_ear,right_ear,left_shoulder,right_shoulder,left_elbow,right_elbow,left_wrist,right_wrist,left_hip,right_hip,left_knee,right_knee,left_ankle,right_ankle,left_big_toe,left_small_toe,left_heel,right_big_toe,right_small_toe,right_heel]
    # 作成するデータフレームのインデックス
    index=['nose','left_eye','right_eye','left_ear','right_ear','left_shoulder','right_shoulder','left_elbow','right_elbow','left_wrist','right_wrist','left_hip','right_hip','left_knee','right_knee','left_ankle','right_ankle','left_big_toe','left_small_toe','left_heel','right_big_toe','right_small_toe','right_heel']
    # pandasでデータフレームを作成する
    df=pd.DataFrame(data=keypoint_list,index=index)
    return df
