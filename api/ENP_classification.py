from flask import Blueprint, jsonify, request

# BluePrintの作成
enp_classifier_bp = Blueprint('enp_classifier', __name__)

@enp_classifier_bp.route('/level', methods=['GET'])
def enp_classifier():
    # クエリパラメータから50m走のタイムを取得
    time_50m = request.args.get('time')

    # タイムが指定されていない場合や無効な場合
    if time_50m is None:
        return jsonify({'error': 'タイムが指定されていません'}), 400
    
    try:
        time_50m = float(time_50m)
    except ValueError:
        return jsonify({'error': 'タイムは数値でなければなりません'}), 400

    # タイムが負の場合は無効とする
    if time_50m <= 0:
        return jsonify({'error': '正のタイムを入力してください'}), 400

    # 各郡の平均タイム
    Excellent_Group = 6.76
    Normal_Group = 7.22
    Poor_Group = 7.76

    # 各郡との差分をとる
    diff_excellent = abs(time_50m - Excellent_Group)
    diff_normal = abs(time_50m - Normal_Group)
    diff_poor = abs(time_50m - Poor_Group)

    # 差分が一番小さいグループの競技レベルに分類する
    if diff_excellent <= diff_normal and diff_excellent <= diff_poor:
        sprint_level = 'Excellent Level'
    elif diff_normal <= diff_excellent and diff_normal <= diff_poor:
        sprint_level = 'Normal Level'
    else:
        sprint_level = 'Poor Level'

    # 結果をJSON形式で返す
    return jsonify({'level': sprint_level})
