'''
11/15 in 2024. Honoka Yada.
MMPoseの2D姿勢推定結果のJSONファイルから座標を取り出して、パラメータを計算する部分を作成(Excel出力まで)
角速度なども入ってる
'''
import json 
import pandas as pd
import numpy as np
import glob
from natsort import natsorted

# データとの紐付け
data_name={
    1:'Abe',
    2:'Ehara',
    3:'Koga',
    4:'Kobayashi',
    5:'Taketoshi',
    6:'Noda',
    7:'Hujiwara1',
    8:'Hujiwara2',
    9:'Miyashiro',
    10:'Yamada',
    11:'Ueda',
    12:'kuwamoto'
}

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

def cal_param(df): # データフレームから角度等のパラメータを計算する関数
    def cal_degree(keypoint_1,keypoint_2,keypoint_3):
        degrees=[]# 角度の推定
        for s in range(len(keypoint_1)):
            # 三点の座標から角度を求める
            a=np.array(keypoint_1[s])
            b=np.array(keypoint_2[s])
            c=np.array(keypoint_3[s])

            # ベクトルを定義
            vec_a = a-b
            vec_c = c-b
            # コサインの計算
            length_vec_a = np.linalg.norm(vec_a)
            length_vec_c = np.linalg.norm(vec_c)
            inner_product = np.inner(vec_a, vec_c)
            cos = inner_product / (length_vec_a * length_vec_c) # type: ignore
            rad = np.arccos(cos)# 角度（ラジアン）の計算
            degree = np.rad2deg(rad)# 弧度法から度数法（rad ➔ 度）への変換
            degrees.append(degree)# 角度のデータを格納

        return degrees
    
    def cal_angle_with_the_horizon(keypoint_1,keypoint_2):# keypoint1に膝、keypoint2に腰の座標が入ることを想定する
        degrees = []
        for s in range(len(keypoint_1)):
            a=np.array(keypoint_1[s])
            b=np.array(keypoint_2[s])
            #keypoint_2[0]=0# keypoint1のXだけを0とした時の座標点
            c=np.array(keypoint_2[s])
            c[0]=0

            # ベクトルは終点ー始点で計算できる############定義ミス
            # vec_a=a-b
            # vec_horizon=c-b

            vec_a=a-b
            vec_horizon=b-c

            # コサインの計算
            length_vec_a = np.linalg.norm(vec_a)
            length_vec_horizon = np.linalg.norm(vec_horizon)
            inner_product = np.inner(vec_a, vec_horizon)
            cos = inner_product / (length_vec_a * length_vec_horizon) # type: ignore

            rad = np.arccos(cos)# 角度（ラジアン）の計算
            degree = np.rad2deg(rad)# 弧度法から度数法（rad ➔ 度）への変換
            degrees.append(degree)# 角度のデータを格納
        return degrees
    
    def cal_angle_with_the_vertical(keypoint_1,keypoint_2):
        
        degrees = []
        for s in range(len(keypoint_1)):
            a=np.array(keypoint_1[s])
            b=np.array(keypoint_2[s])
            #keypoint_2[0]=0# keypoint1のXだけを0とした時の座標点
            c=np.array(keypoint_2[s])
            c[1]=0

            # ベクトルは終点ー始点で計算できる############定義ミス
            # vec_a=a-b
            # vec_horizon=c-b

            vec_a=a-b
            vec_horizon=c-b

            # コサインの計算
            length_vec_a = np.linalg.norm(vec_a)
            length_vec_horizon = np.linalg.norm(vec_horizon)
            inner_product = np.inner(vec_a, vec_horizon)
            cos = inner_product / (length_vec_a * length_vec_horizon) # type: ignore

            rad = np.arccos(cos)# 角度（ラジアン）の計算
            degree = np.rad2deg(rad)# 弧度法から度数法（rad ➔ 度）への変換
            degrees.append(degree)# 角度のデータを格納
        return degrees

    def cal_speed(keypoint_1,FPS_data):
        speeds=[]
        time_step=1/FPS_data
        # 5点移動平均で平滑化を行う
        speeds= np.convolve(keypoint_1, np.ones(5, dtype=int)/5, mode='same')
        speeds=np.diff(keypoint_1)/time_step

        return speeds
    
    def cal_angular_velocity(degrees,FPS_data):
        time_step=1/FPS_data 
        # 5点移動平均で平滑化を行う
        degrees = np.convolve(degrees, np.ones(5, dtype=int)/5, mode='same')
        #degrees = pd.Series(degrees).rolling(window=5, center=True).mean().fillna(method='bfill').fillna(method='ffill').to_numpy()

        # 角度の差分を求める
        #diff_degrees = np.diff(degrees)/time_step
        diff_degrees = np.append(np.nan, np.diff(degrees) / time_step)

        return diff_degrees.tolist()

    # 股関節の角度(14-12-13)※12をとっているのは右側から撮影することを想定しているため
    hip_angle=cal_degree((df.loc['right_knee']).tolist(),(df.loc['right_hip']).tolist(),(df.loc['left_knee']).tolist())

    # 膝の角度 
    left_knee_joint_angle=cal_degree((df.loc['left_hip']).tolist(),(df.loc['left_knee']).tolist(),(df.loc['left_ankle']).tolist())
    right_knee_joint_angle=cal_degree((df.loc['right_hip']).tolist(),(df.loc['right_knee']).tolist(),(df.loc['right_ankle']).tolist())
    # 肩関節の開き
    left_shoulder_angle=cal_degree((df.loc['left_elbow']).tolist(),(df.loc['left_shoulder']).tolist(),(df.loc['left_hip']).tolist())
    right_shoulder_angle=cal_degree((df.loc['right_elbow']).tolist(),(df.loc['right_shoulder']).tolist(),(df.loc['right_hip']).tolist())

    # 大腿部角度(回復角を求める様)
    left_thigh_angle=cal_angle_with_the_horizon((df.loc['left_knee']).tolist(),(df.loc['left_hip']).tolist())
    right_thigh_angle=cal_angle_with_the_horizon((df.loc['right_knee']).tolist(),(df.loc['right_hip']).tolist())

    # 腸腰筋角度
    left_iliopsoas_angle=cal_degree((df.loc['left_shoulder']).tolist(),(df.loc['left_hip']).tolist(),(df.loc['left_knee']).tolist())
    right_iliopsoas_angle=cal_degree((df.loc['right_shoulder']).tolist(),(df.loc['right_hip']).tolist(),(df.loc['right_knee']).tolist())

    # 足関節角度
    left_ankle_joint_angle=cal_degree((df.loc['left_big_toe']).tolist(),(df.loc['left_ankle']).tolist(),(df.loc['left_knee']).tolist())
    right_ankle_joint_angle=cal_degree((df.loc['right_big_toe']).tolist(),(df.loc['right_ankle']).tolist(),(df.loc['right_knee']).tolist())

    # 上腕セグメント角度
    left_upper_arm_segment_angle=cal_angle_with_the_horizon((df.loc['left_elbow']).tolist(),(df.loc['left_shoulder']).tolist())
    right_upper_arm_segment_angle=cal_angle_with_the_horizon((df.loc['right_elbow']).tolist(),(df.loc['right_shoulder']).tolist())

    # 右側からみた体幹部角度
    trunk_angle=cal_angle_with_the_vertical((df.loc['right_hip']).tolist(),(df.loc['right_shoulder']).tolist())

    # 下腿部角度
    left_lower_leg_angle=cal_angle_with_the_vertical((df.loc['left_ankle']).tolist(),(df.loc['left_knee']).tolist())
    right_lower_leg_angle=cal_angle_with_the_vertical((df.loc['right_ankle']).tolist(),(df.loc['right_knee']).tolist())


    # 対象人物の疾走速度
    #speed=cal_speed((df.loc['nose']).tolist(),FPS_data)

    # 腿上げ角速度
    left_thigh_angle_velocity=cal_angular_velocity(cal_angle_with_the_horizon((df.loc['left_knee']).tolist(),(df.loc['left_hip']).tolist()),FPS_data)
    right_thigh_angle_velocity=cal_angular_velocity(cal_angle_with_the_horizon((df.loc['right_knee']).tolist(),(df.loc['right_hip']).tolist()),FPS_data)

    # 腸腰筋角速度
    left_iliopsoas_angle_velocity=cal_angular_velocity(left_iliopsoas_angle,FPS_data)
    right_iliopsoas_angle_velocity=cal_angular_velocity(right_iliopsoas_angle,FPS_data)

    # 膝関節角速度
    left_knee_joint_angle_velocity=cal_angular_velocity(left_knee_joint_angle,FPS_data)
    right_knee_joint_angle_velocity=cal_angular_velocity(right_knee_joint_angle,FPS_data)

    # Swing Leg全体の各速度
    left_leg_swing_velocity=cal_angular_velocity(cal_angle_with_the_vertical((df.loc['left_ankle']).tolist(),(df.loc['left_hip']).tolist()),FPS_data)
    right_leg_swing_velocity=cal_angular_velocity(cal_angle_with_the_vertical((df.loc['right_ankle']).tolist(),(df.loc['right_hip']).tolist()),FPS_data)

    # 肘関節角度
    left_elbow_joint_angle_velocity=cal_angular_velocity(cal_degree((df.loc['left_shoulder']).tolist(),(df.loc['left_elbow']).tolist(),(df.loc['left_wrist']).tolist()),FPS_data)
    right_elbow_joint_angle_velocity=cal_angular_velocity(cal_degree((df.loc['right_shoulder']).tolist(),(df.loc['right_elbow']).tolist(),(df.loc['right_wrist']).tolist()),FPS_data)

    # 上腕セグメント角速度
    left_upper_arm_segment_angle_velocity=cal_angular_velocity(left_upper_arm_segment_angle,FPS_data)
    right_upper_arm_segment_angle_velocity=cal_angular_velocity(right_upper_arm_segment_angle,FPS_data)

    # 足関節角速度
    left_ankle_joint_angle_velocity=cal_angular_velocity(left_ankle_joint_angle,FPS_data)
    right_ankle_joint_angle_velocity=cal_angular_velocity(right_ankle_joint_angle,FPS_data)

    # 計算したパラメータ用のデータフレームを作成
    df_cal_param=pd.DataFrame(data=hip_angle,columns=["hip angle"])
    # 追加した列
    df_cal_param.insert(1,'left knee joint angle',left_knee_joint_angle)
    df_cal_param.insert(2,'right knee joint angle',right_knee_joint_angle)  
    df_cal_param.insert(3,'left shoulder angle',left_shoulder_angle) 
    df_cal_param.insert(4,'right shoulder angle',right_shoulder_angle) 
    df_cal_param.insert(5,'left thigh angle',left_thigh_angle)
    df_cal_param.insert(6,'right thigh angle',right_thigh_angle)
    df_cal_param.insert(7,'left iliopsoas angle',left_iliopsoas_angle)
    df_cal_param.insert(8,'right iliopsoas angle',right_iliopsoas_angle)
    df_cal_param.insert(9,'left ankle joint angle',left_ankle_joint_angle)
    df_cal_param.insert(10,'right ankle joint angle',right_ankle_joint_angle)
    df_cal_param.insert(11,'left upper arm segment angle',left_upper_arm_segment_angle)
    df_cal_param.insert(12,'right upper arm segment angle',right_upper_arm_segment_angle)
    df_cal_param.insert(13,'trunk angle',trunk_angle)
    df_cal_param.insert(14,'left lower leg angle',left_lower_leg_angle)
    df_cal_param.insert(15,'right lower leg angle',right_lower_leg_angle)
    df_cal_param.insert(16,'left thigh angle velocity',left_thigh_angle_velocity)
    df_cal_param.insert(17,'right thigh angle velocity',right_thigh_angle_velocity)
    df_cal_param.insert(18,'left iliopsoas angle velocity',left_iliopsoas_angle_velocity)
    df_cal_param.insert(19,'right iliopsoas angle velocity',right_iliopsoas_angle_velocity)
    df_cal_param.insert(20,'left knee joint angle velocity',left_knee_joint_angle_velocity)
    df_cal_param.insert(21,'right knee joint angle velocity',right_knee_joint_angle_velocity)
    df_cal_param.insert(22,'left leg swing velocity',left_leg_swing_velocity)
    df_cal_param.insert(23,'right leg swing velocity',right_leg_swing_velocity)
    df_cal_param.insert(24,'left elbow joint angle',left_elbow_joint_angle_velocity)
    df_cal_param.insert(25,'right elbow joint angle',right_elbow_joint_angle_velocity)
    df_cal_param.insert(26,'left upper arm segment angle velocity',left_upper_arm_segment_angle_velocity)
    df_cal_param.insert(27,'right upper arm segment angle velocity',right_upper_arm_segment_angle_velocity)
    df_cal_param.insert(28,'left ankle joint angle velocity',left_ankle_joint_angle_velocity)
    df_cal_param.insert(29,'right ankle joint angle velocity',right_ankle_joint_angle_velocity)
    
    return df_cal_param

if __name__=='__main__':

    json_dir = '/Users/honoka/Desktop/研究/241115/support'
    global FPS_data
    FPS_data=240

    json_df =[]

    print("JSONフォルダ内からJSONファイルを検索...")
    for json_file in natsorted(glob.glob(f"{json_dir}/**/*.json")):
        with open(json_file, 'r') as f:
            json_data=json.load(f)
            df_data=json_to_keypoint_df(json_data)
            json_df.append(df_data)
    print('%d 個のJSONファイルを検出しました'%(len(json_df)))
    print('JSONファイルをデータフレームに変換しました')

    # 座標データのカラムとインデックスを入れ替えるリスト
    point_data_df=[]
    for df in json_df:
        df=df.T
        point_data_df.append(df)

    with pd.ExcelWriter("support_original_data.xlsx") as writer:
        for i in range(len(point_data_df)):
            df=point_data_df[i]
            df.to_excel(writer,sheet_name=data_name[i+1])
            print('%d 人目の座標データをExcelファイルに保存しました'% (i+1))

    # パラメーターを計算後のデータを格納するリスト
    param_df = []
    print("座標データからパラメータを計算します")
    for df in json_df:
        cal_df=cal_param(df)
        param_df.append(cal_df)
        print('%d 人目のパラメータの計算が完了しました'% (len(param_df)))

    with pd.ExcelWriter("v4_support_param.xlsx") as writer:
        for i in range(len(param_df)):
            df=param_df[i]
            df.to_excel(writer,sheet_name=data_name[i+1])
            print('%d 人目のパラメータデータをExcelファイルに保存しました'% (i+1))



