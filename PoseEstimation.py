# MMPoseを実行するためのAPI
import os
import subprocess

def execute_MMPose(input_file, output_folder, filename, analyzing_files):    
    # MMPoseの上記のコードを実行できるディレクトリ
    mmpose_dir="/home/imade/yada/241108_new_mmpose/mmpose"

    # 上記のディレクトリに移動する
    os.chdir(mmpose_dir)

    # MMDETはmmdetectionの略
    # トップダウン方式という先に物体検出を使用する方式を使用しているため物体検出のコードも動いている
    run_cmd=f"python3 demo/topdown_demo_with_mmdet.py \
    demo/mmdetection_cfg/rtmdet_m_640-8xb32_coco-person.py \
    https://download.openmmlab.com/mmpose/v1/projects/rtmpose/rtmdet_m_8xb32-100e_coco-obj365-person-235e8209.pth \
    configs/wholebody_2d_keypoint/topdown_heatmap/coco-wholebody/td-hm_hrnet-w48_dark-8xb32-210e_coco-wholebody-384x288.py \
    https://download.openmmlab.com/mmpose/top_down/hrnet/hrnet_w48_coco_wholebody_384x288_dark-f5726563_20200918.pth \
    --input  {input_file} \
    --output-root  {output_folder} \
    --save-predictions"

    subprocess.run(run_cmd,shell=True,check=True)
    analyzing_files.pop(filename, None)  # 解析が終了したら辞書から削除

    return True