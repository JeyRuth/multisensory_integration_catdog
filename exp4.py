from psychopy import visual, core, event, sound
import random
import csv
import json

# ----------------------------
# PARAMÈTRES
# ----------------------------

n_items = 1
noise_levels = [60, 80, 90]

cats = [f"{i+1:02d}s" for i in range(n_items)]
dogs = [f"{i+1:02d}d" for i in range(n_items)]

FIX_MIN = 0.5
FIX_MAX = 1.0
STIM_DUR = 0.5
ISI_DUR = 0.3

# ----------------------------
# FENÊTRE
# ----------------------------

win = visual.Window([1000, 800], color="grey", units='norm')

# ----------------------------
# STIMULI
# ----------------------------

bg = visual.ImageStim(win, image="images/01d_pink_100.png", size=(2, 2))
img = visual.ImageStim(win, size=(2, 2))
fix = visual.TextStim(win, text="+", height=0.08, color='white')

instruction = visual.TextStim(
    win,
    text="S = CHAT | L = CHIEN\nAppuie pour commencer",
    height=0.07
)

# ----------------------------
# AUDIO
# ----------------------------

bg_sound = sound.Sound("sons/pink_noise.wav", loops=-1)
bg_sound.setVolume(1.0)
bg_sound.play()

sounds = {}

def load_sound(path):
    if path not in sounds:
        sounds[path] = sound.Sound(path)
    return sounds[path]

# ----------------------------
# TRIALS
# ----------------------------

trials = []

for noise in noise_levels:
    block = []

    for i in range(n_items):

        block += [
            {"modality": "V", "vis": f"images/{cats[i]}_pink_{noise}.png", "aud": None, "label": "chat", "noise": noise},
            {"modality": "V", "vis": f"images/{dogs[i]}_pink_{noise}.png", "aud": None, "label": "chien", "noise": noise},

            {"modality": "A", "vis": None, "aud": f"sons/cat_{i+1:02d}_pink_{noise}.wav", "label": "chat", "noise": noise},
            {"modality": "A", "vis": None, "aud": f"sons/dog_{i+1:02d}_pink_{noise}.wav", "label": "chien", "noise": noise},

            {"modality": "AV", "vis": f"images/{cats[i]}_pink_{noise}.png", "aud": f"sons/cat_{i+1:02d}_pink_{noise}.wav", "label": "chat", "congruence": "congruent", "noise": noise},
            {"modality": "AV", "vis": f"images/{dogs[i]}_pink_{noise}.png", "aud": f"sons/dog_{i+1:02d}_pink_{noise}.wav", "label": "chien", "congruence": "congruent", "noise": noise},

            {"modality": "AV", "vis": f"images/{cats[i]}_pink_{noise}.png", "aud": f"sons/dog_{i+1:02d}_pink_{noise}.wav", "label": "chien", "congruence": "incongruent", "noise": noise},
            {"modality": "AV", "vis": f"images/{dogs[i]}_pink_{noise}.png", "aud": f"sons/cat_{i+1:02d}_pink_{noise}.wav", "label": "chat", "congruence": "incongruent", "noise": noise},
        ]

    random.shuffle(block)
    trials.extend(block)

random.shuffle(trials)

# ----------------------------
# INSTRUCTIONS
# ----------------------------

instruction.draw()
win.flip()
event.waitKeys()

results = []

# ----------------------------
# EXPÉRIMENT
# ----------------------------

for t in trials:

    event.clearEvents()

    # =========================================================
    # FIXATION
    # =========================================================

    fix.setColor("white")
    fix_dur = random.uniform(FIX_MIN, FIX_MAX)

    clock = core.Clock()
    while clock.getTime() < fix_dur:
        bg.draw()
        fix.draw()
        win.flip()

    # =========================================================
    # STIMULUS
    # =========================================================

    stim_clock = core.Clock()
    snd = load_sound(t["aud"]) if t["aud"] else None
    sound_played = False

    while stim_clock.getTime() < STIM_DUR:

        bg.draw()

        if t["vis"]:
            img.image = t["vis"]
            img.draw()

        fix.draw()
        win.flip()

        if snd and not sound_played:
            snd.play()
            sound_played = True

    # =========================================================
    # ISI
    # =========================================================

    isi_clock = core.Clock()

    while isi_clock.getTime() < ISI_DUR:
        bg.draw()
        fix.draw()
        win.flip()

    # =========================================================
    # RÉPONSE (SANS STIMULUS)
    # =========================================================

    fix.setColor("green")

    resp_clock = core.Clock()
    resp_clock.reset()

    resp = None
    rt = None
    all_keys = []

    while resp is None:

        bg.draw()
        fix.draw()   # uniquement la croix verte
        win.flip()

        keys = event.getKeys(keyList=["s", "l"], timeStamped=resp_clock)

        for key, key_rt in keys:
            all_keys.append({"key": key, "rt": key_rt})

            resp = "chat" if key == "s" else "chien"
            rt = key_rt
            correct = int(resp == t["label"])
            break

    fix.setColor("white")

    # =========================================================
    # SAVE
    # =========================================================

    results.append([
        t["modality"],
        t.get("congruence", "NA"),
        t["noise"],
        t["label"],
        resp,
        correct,
        rt,
        json.dumps(all_keys)
    ])

# ----------------------------
# SAVE FILE
# ----------------------------

with open("data_AV.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["modality","congruence","noise","target","response","correct","RT","all_keys"])
    writer.writerows(results)

# ----------------------------
# END
# ----------------------------

bg_sound.stop()
win.close()
core.quit()