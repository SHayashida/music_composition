#!/usr/bin/env python3
"""
エリック・サティのジムノペディをモチーフにしたアンビエント・ミュージック
・ピアノ曲（MIDI 出力）
・左手の伴奏付き
・楽曲長：約4分（3/4拍子・テンポ60 BPM、80小節）
・主テーマ→展開→主テーマ再現の形式

必要ライブラリ:
    pip install MIDIUtil
"""

from midiutil import MIDIFile

# --- 基本パラメータ ---
tempo = 60                   # BPM（1拍=1秒）
beats_per_measure = 3        # 3/4拍子
total_measures = 80          # 合計80小節（約4分）
track = 0                    # MIDIトラック番号
volume_left = 70             # 左手の音量
volume_right = 80            # 右手（メロディ）の音量

# --- MIDI ファイルオブジェクトの生成 ---
midi = MIDIFile(1)           # 1トラックの MIDI ファイル
midi.addTempo(track, 0, tempo)

# チャンネルの指定（左手：チャンネル0、右手：チャンネル1）
left_channel = 0
right_channel = 1
# プログラムチェンジ（アコースティック・グランドピアノ：プログラム番号0）
midi.addProgramChange(track, left_channel, 0, 0)
midi.addProgramChange(track, right_channel, 0, 0)

# --- 主テーマ用のコード進行（16小節分） ---
# Gymnopédie No.1 の和音進行をイメージして、
# 8小節分の進行を2回繰り返す形にしています。
# なお、各和音は左手用に低音域（おおよそ 40～60 番）に設定しています。
#   ・D (D major): [D3, F#3, A3] → [50, 54, 57]
#   ・A (A major): [A2, C#3, E3] → [45, 49, 52]
#   ・Bm (B minor): [B2, D3, F#3] → [47, 50, 54]
#   ・F#m (F# minor): [F#2, A2, C#3] → [42, 45, 49]
#   ・G (G major): [G2, B2, D3] → [43, 47, 50]
chords_main = [
    {"name": "D",   "notes": [50, 54, 57]},
    {"name": "A",   "notes": [45, 49, 52]},
    {"name": "Bm",  "notes": [47, 50, 54]},
    {"name": "F#m", "notes": [42, 45, 49]},
    {"name": "G",   "notes": [43, 47, 50]},
    {"name": "D",   "notes": [50, 54, 57]},
    {"name": "G",   "notes": [43, 47, 50]},
    {"name": "A",   "notes": [45, 49, 52]},
]
# 8小節分の進行を2回繰り返して 16小節分に
chords_main_full = chords_main * 2  # 長さ16

# --- 展開部用のコード進行（48小節分） ---
# 4小節のパターンを12回繰り返す
chords_dev_cycle = [
    {"name": "Bm", "notes": [47, 50, 54]},
    {"name": "G",  "notes": [43, 47, 50]},
    {"name": "D",  "notes": [50, 54, 57]},
    {"name": "A",  "notes": [45, 49, 52]},
]
chords_dev_full = chords_dev_cycle * 12  # 長さ48

# --- 補助関数 ---
def add_left_hand(midi_obj, start_measure, num_measures, chords_list, channel):
    """
    左手の伴奏を各小節に追加します。
    各小節では、対象和音の各音を 1 拍ずつ順に鳴らすアルペジオ風パターンです。
    """
    for i in range(num_measures):
        measure = start_measure + i
        time = measure * beats_per_measure  # 小節の開始拍（単位：拍）
        chord = chords_list[i]  # 対応する和音（小節ごとに異なる）
        # 1小節の各拍（0, 1, 2拍目）に和音の各音を鳴らす
        for j, note in enumerate(chord["notes"]):
            note_time = time + j  # j 拍目に開始
            midi_obj.addNote(track, channel, note, note_time, 1, volume_left)

def add_right_hand_main(midi_obj, start_measure, num_measures, chords_list, channel):
    """
    主テーマ部の右手メロディを追加します。
    各小節で、和音の各音を1オクターブ上げたものからなる固定のモチーフを用います。
    モチーフ（4音）の発音タイミングは小節内のオフセット [0.5, 1.25, 2.0, 2.75] 拍です。
    """
    offsets = [0.5, 1.25, 2.0, 2.75]
    for i in range(num_measures):
        measure = start_measure + i
        time = measure * beats_per_measure
        chord = chords_list[i]
        # メロディ・モチーフ：和音の各音を1オクターブ上げたもの（ただし2番目の音を重ねる）
        melody_notes = [
            chord["notes"][0] + 12,
            chord["notes"][1] + 12,
            chord["notes"][2] + 12,
            chord["notes"][1] + 12
        ]
        for offset, note in zip(offsets, melody_notes):
            midi_obj.addNote(track, channel, note, time + offset, 0.75, volume_right)

def add_right_hand_development(midi_obj, start_measure, num_measures, chords_list, channel):
    """
    展開部の右手メロディを追加します。
    主テーマとは異なるリズムと音順の変化を加えたモチーフを用います。
    各小節で、発音タイミングは [0.25, 1.0, 1.75, 2.5] 拍です。
    モチーフは、対象和音の音を1オクターブ上げたものから、
    [2番目, 3番目, 1番目, 3番目] の順に採用しています。
    """
    offsets = [0.25, 1.0, 1.75, 2.5]
    for i in range(num_measures):
        measure = start_measure + i
        time = measure * beats_per_measure
        chord = chords_list[i]
        melody_notes = [
            chord["notes"][1] + 12,
            chord["notes"][2] + 12,
            chord["notes"][0] + 12,
            chord["notes"][2] + 12
        ]
        for offset, note in zip(offsets, melody_notes):
            midi_obj.addNote(track, channel, note, time + offset, 0.75, volume_right)

# --- 楽曲構造に沿った各部の追加 ---
# 主テーマ部（最初の16小節）
main_start = 0
main_measures = 16
add_left_hand(midi, main_start, main_measures, chords_main_full, left_channel)
add_right_hand_main(midi, main_start, main_measures, chords_main_full, right_channel)

# 展開部（次の48小節）
dev_start = main_measures  # 16小節目の後から
dev_measures = 48
add_left_hand(midi, dev_start, dev_measures, chords_dev_full, left_channel)
add_right_hand_development(midi, dev_start, dev_measures, chords_dev_full, right_channel)

# 主テーマ部の再現（最後の16小節）
final_main_start = main_measures + dev_measures  # 64小節目から
final_main_measures = 16
add_left_hand(midi, final_main_start, final_main_measures, chords_main_full, left_channel)
add_right_hand_main(midi, final_main_start, final_main_measures, chords_main_full, right_channel)

# --- MIDI ファイルの出力 ---
with open("satie_ambient.mid", "wb") as output_file:
    midi.writeFile(output_file)

print("MIDIファイル 'satie_ambient.mid' を出力しました。")
