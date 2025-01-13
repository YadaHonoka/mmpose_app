// アップロード後にビデオを表示するためのJavaScript
document.getElementById("uploadForm").onsubmit = function(event) {
    // フォームが送信されたときの処理
    event.preventDefault(); // フォームのデフォルトの送信動作を防ぐ
    // FormDataオブジェクトを作成
    var formData = new FormData(document.getElementById("uploadForm")); // フォームデータを取得
    
    var time = document.getElementById('time').value;
    localStorage.setItem("time",time);

    // フォームデータをサーバーに送信
    // fetch関数を使って非同期通信を行う
    // fetch関数はPromiseを返す
    fetch('/upload', {// fetch関数の第一引数にはリクエストを送信するURLを指定
        method: 'POST',// fetch関数の第二引数にはリクエストの設定を指定
        body: formData// リクエストのボディにフォームデータを指定
    // リクエストのヘッダーにフォームデータの形式を指定
    })
    .then(response => response.json()) // レスポンスをJSON形式に変換
    // レスポンスのJSONデータをコンソールに出力
    .then(data => {// レスポンスのJSONデータをコンソールに出力
          if (data.video_url) { // レスポンスのJSONデータにvideo_urlが含まれている場合
            console.log('Video URL:', data.video_url); // 動画URLをコンソールに出力
            document.getElementById('videoSource').src = data.video_url; // 動画のソースを設定
            var videoPlayer = document.getElementById('videoPlayer');// 動画プレイヤーを取得
            videoPlayer.style.display = 'block'; // 動画プレイヤーを表示 // 動画プレイヤーを再生
            videoPlayer.load(); // 動画プレイヤーを再読み込み
            document.getElementById('timeResult').innerText = `50m走タイム: ${data.time}秒`; // タイムを表示
            document.getElementById('editForm').style.display = 'block'; // 編集フォームを表示
            
            // 動画のメタデータが読み込まれた後にスライダーを初期化
            videoPlayer.addEventListener('loadedmetadata', function() {
                // noUiSliderの設定 // https://refreshless.com/nouislider/
                var slider = document.getElementById('slider');
                noUiSlider.create(slider, { // noUiSliderを作成
                    start: [0, videoPlayer.duration], // スライダーの初期値を設定 // 開始時間と終了時間 // 動画の長さ
                    connect: true, // スライダーのつなぎ目を表示
                    range: {
                        'min': 0,
                        'max': videoPlayer.duration
                    },
                    step: 0.001 // ステップを小さくして感度を上げる
                });

                // スライダーの値が更新されたときの処理
                slider.noUiSlider.on('update', function(values, handle) {
                    // スライダーの値が更新されたときの処理 
                    // 値とハンドルを引数に取る7 
                    // ハンドルはスライダーのハンドルの数 
                    // 値はスライダーの値の配列 
                    // 開始時間と終了時間
                    // 動画の再生位置を設定
                    if (handle === 0) { // ハンドルが0の場合
                        videoPlayer.currentTime = values[0]; // 動画の再生位置を設定
                    } else {
                        videoPlayer.currentTime = values[1]; // 動画の再生位置 // ハンドルが1の場合   
                    }
                });

                  // スライダーの値が変更されたときの処理
                  slider.noUiSlider.on('change', function(values, handle) { // スライダーの値が変更されたときの処理 // 値とハンドルを引数に取る // ハンドルはスライダーのハンドルの数
                      videoPlayer.currentTime = values[handle]; // 動画の再生位置を設定
                });
            });
        }
    })
    .catch(error => console.log(error)); // エラーをコンソールに出力
};

// カットボタンがクリックされたときの処理
document.getElementById("cutButton").onclick = function() { // カットボタンがクリックされたときの処理
    var slider = document.getElementById('slider'); // スライダーを取得
    var startTime = parseFloat(slider.noUiSlider.get()[0]); // 開始時間を取得
    var endTime = parseFloat(slider.noUiSlider.get()[1]); // 終了時間を取得
    var videoPlayer = document.getElementById('videoPlayer'); // 動画プレイヤーを取得 // 動画の長さ
    
    // 無効な時間範囲の場合はアラートを表示
    if (startTime >= endTime || startTime < 0 || endTime > videoPlayer.duration) { // 無効な時間範囲の場合はアラートを表示
        alert('無効な時間範囲です');
        return;
    }

    var videoUrl = document.getElementById('videoSource').src; // 動画URLを取得
    fetch('/cut', { // fetch関数を使って非同期通信を行う
        method: 'POST', // fetch関数の第一引数にはリクエストを送信するURLを指定
        headers: { //   fetch関数の第二引数にはリクエストの設定を指定
            'Content-Type': 'application/json' // リクエストのヘッダーにJSON形式を指定
        }, 
        body: JSON.stringify({ // リクエストのボディにカットする動画の情報を指定
            video_url: videoUrl, // 動画URL
            start_time: startTime, // 開始時間
            end_time: endTime // 終了時間
        })
    }).then(response => response.json()) // レスポンスをJSON形式に変換
      .then(data => { // レスポンスのJSONデータをコンソールに出力
          if (data.success) { // レスポンスのJSONデータにsuccessが含まれている場合
              alert('動画がカットされました'); // アラートを表示
              document.getElementById('videoSource').src = data.new_video_url; // 動画のソースを設定
              document.getElementById('videoSource').load(); // 動画を再読み込み
              var downloadButton = document.getElementById('downloadButton'); // ダウンロードボタンを取得
              downloadButton.href = data.new_video_url; // ダウンロードボタンのリンクを設定
              downloadButton.style.display = 'block'; // ダウンロードボタンを表示
          } else { //   レスポンスのJSONデータにsuccessが含まれていない場合
              alert('動画のカットに失敗しました'); // アラートを表示
          }
      })
      .catch(error => console.log(error)); // エラーをコンソールに出力
};
