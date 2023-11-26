from flask import Flask, Response, jsonify
from video_server.video_preprocessor import process_videos, get_video_data

app = Flask(__name__)

FRAME_SIZE = (480, 320)

# 处理视频文件
video_data = process_videos("movies", FRAME_SIZE)

@app.route('/channel_info')
def get_channel_lengths():
    lengths = [len(audio) for audio, frames in video_data]
    return jsonify(lengths)

@app.route('/audio/<int:channel_index>/<int:start>/<int:length>')
def get_audio(channel_index, start, length):
    audio, frames = video_data[channel_index % len(video_data)]
    end = start + length
    if end > len(audio):
        end = len(audio)
    if start > end:
        start = end
    if start == end:
        # 不返回任何内容 - 我们没有更多数据可提供
        return Response(b'', mimetype='audio/x-raw')
    slice = audio[start:end]
    return Response(slice, mimetype='audio/x-raw')

@app.route('/frame/<int:channel_index>/<int:ms>')
def get_frame(channel_index, ms):
    audio, frames = video_data[channel_index % len(video_data)]
    # 使用二分搜索找到最接近的帧
    start = 0
    end = len(frames) - 1
    while start <= end:
        mid = (start + end) // 2
        if frames[mid][0] == ms:
            return Response(frames[mid][1], mimetype='image/jpeg')
        elif frames[mid][0] < ms:
            start = mid + 1
        else:
            end = mid - 1
    # 我们可能找不到确切的帧，因此返回最接近的帧
    if end < 0:
        end = 0
    elif start >= len(frames):
        start = len(frames) - 1
    return Response(frames[start][1], mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='192.168.0.107', port=8123)
