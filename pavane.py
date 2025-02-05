from midiutil import MIDIFile

# --- 基本パラメータ設定 ---
track = 0
channel = 0         # ピアノの場合、通常はチャンネル0
tempo = 60          # BPM 60：1拍が1秒なので、ゆったりとしたパヴァーヌの雰囲気に
volume = 100        # メロディの音量（和音は半音量程度に調整）

# 1トラックの MIDI ファイルを作成
midi = MIDIFile(1)
midi.addTempo(track, 0, tempo)

# --- ヘルパー関数 ---
def add_main_theme(midi, start_time, measures, track, channel, volume):
    """
    【主題部】
    穏やかで優しい主題。右手（高音域）でモチーフを刻み、左手（低音域）で和音を伴奏します。
    
    主題モチーフ（例）： D4, F4, A4, C5, A4, F4, D4
    （MIDIノート番号：C4=60 として、D4=62, F4=65, A4=69, C5=72）
    
    各小節は4拍とし、和音は1小節全体にわたって持続させます。
    また、6小節ごとに以下の和音進行を繰り返します：
      1. Dm   (D3, F3, A3)　　→　[50, 53, 57]
      2. Dm   (D3, F3, A3)
      3. Bb   (Bb3, D4, F4)　　→　[58, 62, 65]
      4. C    (C4, E4, G4)　　→　[60, 64, 67]
      5. A7   (A2, C#3, E3, G3) →　[45, 49, 52, 55]
      6. Dm   (D3, F3, A3)　　→　[50, 53, 57]
    """
    measure_duration = 4  # 4拍
    # 主題モチーフ：各タプルは (MIDIノート, 持続拍数)
    motif = [(62, 0.5), (65, 0.5), (69, 1), (72, 0.5), (69, 0.5), (65, 0.5), (62, 0.5)]
    
    # 和音進行（6小節周期）
    chords_main = [
        [50, 53, 57],      # Dm
        [50, 53, 57],      # Dm
        [58, 62, 65],      # Bb（Bb3, D4, F4）
        [60, 64, 67],      # C（C4, E4, G4）
        [45, 49, 52, 55],   # A7（A2, C#3, E3, G3）
        [50, 53, 57]       # Dm
    ]
    num_cycles = measures // 6  # 6小節ごとの繰り返し
    current_time = start_time
    for cycle in range(num_cycles):
        for chord in chords_main:
            # 左手：和音を小節全体にわたって（音量を半分に）
            for note in chord:
                midi.addNote(track, channel, note, current_time, measure_duration, volume // 2)
            # 右手：主題モチーフを刻む
            t = current_time
            for note, dur in motif:
                midi.addNote(track, channel, note, t, dur, volume)
                t += dur
            current_time += measure_duration
    return current_time

def add_development_section(midi, start_time, measures, track, channel, volume):
    """
    【発展部】
    主題から展開し、「天から光が差し込む」様子をイメージしたパートです。
    
    ここでは、左手はゆったりとした Dm のペダル音（和音）を刻み、
    右手は上昇するアルペジオ（例：基音から4度、7度、そしてオクターブ上＋）を順次刻んでいくことで、
    徐々に高まる光のイメージを表現します。
    """
    measure_duration = 4
    current_time = start_time
    for i in range(measures):
        # 左手：安定した Dm 和音（ペダル）をバックに
        chord = [50, 53, 57]  # Dm
        for note in chord:
            midi.addNote(track, channel, note, current_time, measure_duration, volume // 2)
        # 右手：上昇するアルペジオ
        # i が進むごとに基音を少しずつ上げることで、光が降り注ぐイメージを付与
        base_pitch = 62 + (i // 2)  # 2小節ごとに 1 音上昇
        arpeggio = [base_pitch, base_pitch + 4, base_pitch + 7, base_pitch + 12]
        t = current_time
        note_duration = measure_duration / len(arpeggio)
        for note in arpeggio:
            midi.addNote(track, channel, note, t, note_duration, volume)
            t += note_duration
        current_time += measure_duration
    return current_time

# --- 作曲の構成 ---
current_time = 0
main_measures = 30          # 主題部：30小節（約2分）
development_measures = 30   # 発展部：30小節（約2分）
recapitulation_measures = 30  # 再現部：30小節（約2分）

# セクション 1：主題部
current_time = add_main_theme(midi, current_time, main_measures, track, channel, volume)

# セクション 2：発展部（天から光が差し込む様子を表現）
current_time = add_development_section(midi, current_time, development_measures, track, channel, volume)

# セクション 3：再現部（主題へしっかりと回帰）
current_time = add_main_theme(midi, current_time, recapitulation_measures, track, channel, volume)

# --- MIDI ファイル出力 ---
with open("pavane_for_the_deceased_princess.mid", "wb") as output_file:
    midi.writeFile(output_file)

print("MIDIファイル『pavane_for_the_deceased_princess.mid』が作成されました。")
