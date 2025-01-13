from flask import Flask, request, send_file, jsonify, render_template, url_for, send_from_directory
from flask_cors import CORS
import random
import os
import subprocess
import threading  # スレッドを使用するためのモジュール
# 解析用のライブラリをインポート
import cv2  # OpenCVを使用する例
from datetime import datetime, timedelta
import pandas as pd
from PoseEstimation import execute_MMPose
import shutil
from flask import Blueprint, jsonify, request
from api.ENP_classification import enp_classifier_bp


app = Flask(__name__)
CORS(app)  # CORSを有効にする

# BluePrintの登録
app.register_blueprint(enp_classifier_bp)

# アップロードされたファイルを保存するディレクトリを設定
UPLOAD_FOLDER = '/tmp/uploads'
CUT_FOLDER = '/tmp/cuts'
ANALYSIS_FOLDER = '/tmp/analysis'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ディレクトリが存在しない場合は作成
os.makedirs(CUT_FOLDER, exist_ok=True)  # ディレクトリが存在しない場合は作成
os.makedirs(ANALYSIS_FOLDER, exist_ok=True)  # ディレクトリが存在しない場合は作成
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CUT_FOLDER'] = CUT_FOLDER
app.config['ANALYSIS_FOLDER'] = ANALYSIS_FOLDER

# 解析中のファイルを管理するための辞書
analyzing_files = {}

@app.route('/')
def index():
    # index.htmlテンプレートをレンダリングして返す
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # リクエストにファイルが含まれているか確認
    if 'videoFile' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['videoFile']
    
    # ファイル名が空でないか確認
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file:
        # ファイルの拡張子をチェック
        if not (file.filename.lower().endswith('.mp4') or file.filename.lower().endswith('.mov')):
            return jsonify({'error': 'Invalid file type. Only mp4 and mov files are allowed.'})
        
        # 新しいファイル名を取得し、拡張子を付ける
        new_filename = request.form.get('newFilename', file.filename)
        if not new_filename.lower().endswith('.mp4') and not new_filename.lower().endswith('.mov'):
            new_filename += '.mp4'
        
        # ファイルを保存するパスを設定
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)  # ファイルを保存
        
        # 動画ファイルのURLを生成
        video_url = url_for('uploaded_video', filename=new_filename, _external=True)
        
        # 動画のURLと50m走のタイムをJSON形式で返す
        return jsonify({'video_url': video_url, 'time': request.form['time']})

@app.route('/uploaded_video/<filename>')
def uploaded_video(filename):
    # 指定されたファイルを保存ディレクトリから送信
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/video/<filename>')
def video_file(filename):
    # 指定されたファイルを保存ディレクトリから送信
    return send_from_directory(app.config['CUT_FOLDER'], filename)#, as_attachment=True)

@app.route('/analyzed_video/<foldername>/<filename>')
def analyzed_video_file(foldername, filename):
    # 動画の保存場所
    folder_path = os.path.join(app.config['ANALYSIS_FOLDER'], foldername)
    app.config['ANALYSIS_DATA'] = folder_path
    app.logger.debug(folder_path)
    return send_from_directory(app.config['ANALYSIS_DATA'], filename)

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    # 指定されたファイルを削除
    filepath = os.path.join(app.config['CUT_FOLDER'], filename) # ファイルのパスを取得
    if os.path.exists(filepath): # ファイルが存在するか確認
        os.remove(filepath)  # ファイルを削除
        return jsonify({'success': True})   # 削除が成功したことをJSON形式で返す
    else:  # ファイルが存在しない場合はエラーを返す
        return jsonify({'error': 'File not found'}), 404    # 404エラーを返す

@app.route('/delete_all', methods=['DELETE'])
def delete_all_files():
    # アップロードされたすべてのファイルを削除
    for folder in [app.config['UPLOAD_FOLDER'], app.config['CUT_FOLDER']]:
        files = os.listdir(folder) # ファイルのリストを取得
        for file in files: # ファイルを1つずつ削除
            filepath = os.path.join(folder, file) # ファイルのパスを取得
            if os.path.exists(filepath): # ファイルが存在するか確認 
                if os.path.isdir(filepath): # ディレクトリの場合は中のファイルも削除
                    for subfile in os.listdir(filepath):
                        os.remove(os.path.join(filepath, subfile))
                os.remove(filepath) # ファイルを削除
    
    shutil.rmtree(app.config['ANALYSIS_FOLDER'])  # 解析ファイルを削除
    return jsonify({'success': True})

@app.route('/uploads')
def list_uploads():
    # カット編集されたファイルのリストを取得し、時系列順にソート
    files = os.listdir(app.config['CUT_FOLDER']) # ファイルのリストを取得
    files = [file for file in files if file.lower().endswith('.mp4') and not file.startswith('hpe_')]  # mp4ファイルのみをフィルタリング
    files.sort(key=lambda x: os.path.getmtime(os.path.join(app.config['CUT_FOLDER'], x)), reverse=True)
    file_urls = [url_for('video_file', filename=file, _external=True) for file in files]
    return render_template('uploads.html', files=file_urls)

@app.route('/cut', methods=['POST'])
def cut_video():
    data = request.get_json()
    video_url = data['video_url']
    start_time = data['start_time']
    end_time = data['end_time']
    
    filename = video_url.split('/')[-1]
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    new_filename = f"cut_{filename.split('.')[0]}.mp4"
    new_filepath = os.path.join(app.config['CUT_FOLDER'], new_filename)
    
    # FFmpegコマンドを実行して動画をカットし、mp4に変換
    command = [
        'ffmpeg', '-i', filepath, '-ss', str(start_time), '-to', str(end_time),
        '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental', new_filepath
    ]
    
    try:
        subprocess.run(command, check=True)
        new_video_url = url_for('video_file', filename=new_filename, _external=True)
        return jsonify({'success': True, 'new_video_url': new_video_url})
    except subprocess.CalledProcessError:
        return jsonify({'success': False}), 500

@app.route('/analyze/<filename>', methods=['GET'])
def analyze_video(filename): 
    filepath = os.path.join(app.config['CUT_FOLDER'], filename) # ファイルのパスを取得
    if not os.path.exists(filepath): # ファイルが存在するか確認
        return jsonify({'error': 'File not found'}), 404    # 404エラーを返す
    
    filename = filename.split('.')[0] # 拡張子を除いたファイル名を取得
    # MMPoseで加工した動画を保存するパス
    hpe_folder_name = f"hpe_{filename}"
    hpe_filepath = os.path.join(app.config['ANALYSIS_FOLDER'], hpe_folder_name)

    # 解析中の表示を行うために一旦レスポンスを返す
    if filename not in analyzing_files: # すでに解析中の場合は何もしない
        analyzing_files[filename] = True # 解析中のファイルを辞書に追加
        threading.Thread(target=execute_MMPose, args=(filepath, hpe_filepath, filename, analyzing_files)).start() # 解析処理を別スレッドで実行 
    return render_template('analyzing.html', filename=f"{filename}.mp4") # 解析中のページを表示

@app.route('/analyze_result/<filename>', methods=['GET'])
def analyze_result(filename):
    app.logger.debug(filename)
    hpe_folder = f"hpe_{filename.split('.')[0]}"
    filepath = os.path.join(app.config['ANALYSIS_FOLDER'], hpe_folder)
    filepath = os.path.join(filepath, filename)

    app.logger.debug(filepath)

    hpe_video_url = url_for('analyzed_video_file', foldername=hpe_folder, filename=filename, _external=True)
    app.logger.debug(hpe_video_url)
    if not os.path.exists(filepath):
        return render_template('no_analysis.html', filename=filename)
    else:
        return render_template('analysis.html', filename=filename, hpe_video_url=hpe_video_url)

# Pandasを使って時系列データを計算するAPI
@app.route('/api/data')
def get_data():
    # 基準日を設定（例えば、2023年1月1日）
    start_date = datetime(2023, 1, 1)
    
    # 6ヶ月分のデータを生成 (30日単位で進める)
    date_range = pd.date_range(start=start_date, periods=6, freq='M')
    
    # ランダムな数値データを生成 (ここでは単純なランダムな値)
    values = [random.randint(10, 100) for _ in range(6)]

    # PandasのDataFrameを使ってデータを作成
    df = pd.DataFrame({
        'date': date_range,
        'value': values
    })

    # DataFrameをJSON形式に変換して返す
    data = {
        'dates': df['date'].dt.strftime('%Y-%m-%d').tolist(),  # 日付を文字列に変換
        'values': df['value'].tolist()  # 数値データ
    }

    return jsonify(data)


if __name__ == '__main__':
    # アプリケーションを起動
    app.run(host='0.0.0.0', port=5000, debug=True)