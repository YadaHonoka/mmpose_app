import pandas as pd
import numpy as np

def cal_param(df, FPS_data): # データフレームから角度等のパラメータを計算する関数
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
