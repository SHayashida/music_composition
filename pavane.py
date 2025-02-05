from midiutil import MIDIFile

# --- 基本パラメータ ---
track = 0
channel = 0        # ピアノの場合は通常チャンネル0
tempo = 60         # BPM 60：1拍＝1秒、ゆったりとした雰囲気
volume = 100       # メロディの音量（伴奏は半音量で表現）
measure_duration = 4  # 各小節4拍

# --- MIDIファイル作成 ---
midi = MIDIFile(1)
midi.addTempo(track, 0, tempo)

# --- モチーフとコード進行の定義 ---
# オリジナル・モチーフ（右手）： D4, F4, A4, C5, A4, F4, D4
motif_original = [(62, 0.5), (65, 0.5), (69, 1), (72, 0.5), (69, 0.5), (65, 0.5), (62, 0.5)]
# バリエーション・モチーフ（第2音を若干変更）
motif_variant  = [(62, 0.5), (67, 0.5), (69, 1), (72, 0.5), (69, 0.5), (65, 0.5), (62, 0.5)]

# A型コード進行： Dm – Dm – Bb – C – A7 – Dm
progression_A = [
    [50, 53, 57],        # Dm (D3, F3, A3)
    [50, 53, 57],        # Dm
    [58, 62, 65],        # Bb (Bb3, D4, F4)
    [60, 64, 67],        # C  (C4, E4, G4)
    [45, 49, 52, 55],     # A7 (A2, C#3, E3, G3)
    [50, 53, 57]         # Dm
]

# B型コード進行： Dm – Gm – Bb – A7 – F – Dm
progression_B = [
    [50, 53, 57],        # Dm
    [55, 58, 62],        # Gm (G3, Bb3, D4)
    [58, 62, 65],        # Bb
    [45, 49, 52, 55],     # A7
    [53, 57, 60],        # F (F3, A3, C4)
    [50, 53, 57]         # Dm
]

# --- セクション1: エクスポジション（主題部） ---
def add_exposition_section(midi, start_time, measures, track, channel, volume):
    """
    エクスポジション部：  
    6小節ごとのサイクルで、A型とB型のコード進行およびモチーフ（オリジナルと変化形）を交互に配置します。
    """
    current_time = start_time
    cycle_length = 6  # 6小節のサイクル
    num_cycles = measures // cycle_length
    for cycle in range(num_cycles):
        # サイクルごとに使用する進行とモチーフを決定
        if cycle % 2 == 0:
            progression = progression_A
            motif = motif_original
        else:
            progression = progression_B
            motif = motif_variant
        # 6小節分ループ
        for chord in progression:
            # 左手：伴奏として和音（音量は控えめに）
            for note in chord:
                midi.addNote(track, channel, note, current_time, measure_duration, volume // 2)
            # 右手：モチーフを刻む（小節内に収まるように）
            t = current_time
            for note, dur in motif:
                midi.addNote(track, channel, note, t, dur, volume)
                t += dur
            current_time += measure_duration
    return current_time

# --- セクション2: 発展部 ---
def add_development_section(midi, start_time, measures, track, channel, volume):
    """
    発展部：  
    右手は、天から光が差し込むような印象を与えるため、上昇と下降を交互に行うアルペジオを配置。
    左手は、Dmのペダル音を持続させつつ、基音が徐々に上昇していくように設定。
    """
    current_time = start_time
    for i in range(measures):
        # 左手：安定した Dm の和音
        for note in [50, 53, 57]:
            midi.addNote(track, channel, note, current_time, measure_duration, volume // 2)
        # 基本の基音を徐々に上昇（2小節ごとに1音上昇）
        base_pitch = 62 + (i // 2)
        # 奇数小節は下降、偶数小節は上昇のアルペジオ
        if i % 2 == 0:
            arpeggio = [base_pitch, base_pitch + 4, base_pitch + 7, base_pitch + 12]
        else:
            arpeggio = [base_pitch + 12, base_pitch + 7, base_pitch + 4, base_pitch]
        note_dur = measure_duration / len(arpeggio)
        t = current_time
        for note in arpeggio:
            midi.addNote(track, channel, note, t, note_dur, volume)
            t += note_dur
        current_time += measure_duration
    return current_time

# --- セクション3: 転調部（ブリッジ） ---
def add_transition_section(midi, start_time, measures, track, channel, volume):
    """
    転調部：  
    発展部から再現部へと戻るための4小節のブリッジ。  
    右手は高音から徐々に下行するクロマチックなラインで、調性を安定させる。
    最後の小節で Dm を強調します。
    """
    current_time = start_time
    # 最初の3小節：クロマチック下降のメロディ
    for i in range(measures - 1):
        # 1小節分、4拍に分けて下降
        start_pitch = 74 - i*2  # 高音からスタートし、徐々に下がる
        for beat in range(4):
            pitch = start_pitch - beat
            midi.addNote(track, channel, pitch, current_time + beat, 1, volume)
        current_time += measure_duration
    # 最終小節：Dmの和音をしっかり配置して回帰感を強調
    for note in [50, 53, 57]:
        midi.addNote(track, channel, note, current_time, measure_duration, volume)
    # 同時に、右手で短いモチーフ（オリジナル）を配置
    t = current_time
    for note, dur in motif_original:
        midi.addNote(track, channel, note, t, dur, volume)
        t += dur
    current_time += measure_duration
    return current_time

# --- セクション4: 再現部 ---
def add_recapitulation_section(midi, start_time, measures, track, channel, volume):
    """
    再現部：  
    エクスポジション部のオリジナルのコード進行（A型）とモチーフで、  
    主題の確固たる回帰と、優しい王女のイメージを強調します。
    """
    current_time = start_time
    # ここでは progression_A と motif_original を固定的に用いる
    num_cycles = measures // 6
    for cycle in range(num_cycles):
        for chord in progression_A:
            for note in chord:
                midi.addNote(track, channel, note, current_time, measure_duration, volume // 2)
            t = current_time
            for note, dur in motif_original:
                midi.addNote(track, channel, note, t, dur, volume)
                t += dur
            current_time += measure_duration
    return current_time

# --- 全体の構成 ---
# エクスポジション：30小節
# 発展部：30小節
# 転調部：4小節
# 再現部：30小節

current_time = 0
current_time = add_exposition_section(midi, current_time, 30, track, channel, volume)
current_time = add_development_section(midi, current_time, 30, track, channel, volume)
current_time = add_transition_section(midi, current_time, 4, track, channel, volume)
current_time = add_recapitulation_section(midi, current_time, 30, track, channel, volume)

# --- MIDI ファイル出力 ---
with open("luminous_reminiscence.mid", "wb") as output_file:
    midi.writeFile(output_file)

print("MIDIファイル『luminous_reminiscence.mid』が作成されました。")
