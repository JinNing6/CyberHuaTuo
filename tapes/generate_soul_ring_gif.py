"""
🔮 魂环全息投影动画 GIF 生成器 v2 — 炫酷增强版
Soul Ring Hologram Animation GIF Generator v2 — Enhanced Edition

使用 Pillow 直接绘制图形级同心圆旋转动画。
特效包括：星空背景、环辉光、能量脉冲波、HUD 科幻边框、
轨道亮标、粒子拖尾、环间电弧。

用法：
    python tapes/generate_soul_ring_gif.py
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# 配置参数
# ============================================================

WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
BG_COLOR = (10, 10, 20)
TOTAL_FRAMES = 80
FPS = 15

# 魂环定义 (bright_color, dim_color, glow_color, radius, width, name)
RING_DEFS = [
    ((255, 255, 255), (80, 80, 90),   (200, 200, 220), 80,  6, "白环"),
    ((255, 200, 50),  (120, 90, 20),  (255, 220, 80),  130, 7, "黄环"),
    ((255, 200, 50),  (120, 90, 20),  (255, 220, 80),  180, 7, "黄环"),
    ((180, 80, 255),  (80, 30, 140),  (200, 120, 255), 230, 8, "紫环"),
    ((180, 80, 255),  (80, 30, 140),  (200, 120, 255), 280, 8, "紫环"),
]

CORE_COLOR = (255, 200, 50)
CORE_GLOW = (255, 220, 100)
TEXT_COLOR = (0, 255, 200)
TEXT_DIM = (0, 140, 110)
GOLD_TEXT = (255, 200, 50)
CYAN = (0, 255, 200)
CYAN_DIM = (0, 80, 60)


def lerp_color(c1, c2, t):
    """线性插值两种颜色，t 被 clamp 到 [0,1]"""
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ============================================================
# 特效 1：星空背景
# ============================================================

def _gen_stars(count=200):
    """预生成固定星位"""
    rng = random.Random(1337)
    stars = []
    for _ in range(count):
        x = rng.randint(0, WIDTH - 1)
        y = rng.randint(0, HEIGHT - 1)
        brightness = rng.uniform(0.2, 1.0)
        twinkle_speed = rng.uniform(0.05, 0.2)
        twinkle_phase = rng.uniform(0, 2 * math.pi)
        stars.append((x, y, brightness, twinkle_speed, twinkle_phase))
    return stars

STARS = _gen_stars()


def draw_starfield(draw, frame):
    """绘制闪烁星空"""
    for x, y, base_b, speed, phase in STARS:
        b = base_b * (0.5 + 0.5 * math.sin(frame * speed + phase))
        v = int(200 * b)
        color = (v, v, int(v * 1.1))  # 略偏蓝
        r = 0.5 + b * 0.6
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


# ============================================================
# 特效 2：HUD 科幻边框
# ============================================================

def draw_hud_frame(draw, frame):
    """绘制四角瞄准框 + 扫描线"""
    corner_len = 40
    gap = 20  # 距边缘

    # 角框颜色随帧闪烁
    alpha = 0.5 + 0.5 * math.sin(frame * 0.15)
    c = lerp_color(CYAN_DIM, CYAN, alpha)

    # 四个角
    corners = [
        # 左上
        [(gap, gap), (gap + corner_len, gap), (gap, gap), (gap, gap + corner_len)],
        # 右上
        [(WIDTH - gap, gap), (WIDTH - gap - corner_len, gap),
         (WIDTH - gap, gap), (WIDTH - gap, gap + corner_len)],
        # 左下
        [(gap, HEIGHT - gap), (gap + corner_len, HEIGHT - gap),
         (gap, HEIGHT - gap), (gap, HEIGHT - gap - corner_len)],
        # 右下
        [(WIDTH - gap, HEIGHT - gap), (WIDTH - gap - corner_len, HEIGHT - gap),
         (WIDTH - gap, HEIGHT - gap), (WIDTH - gap, HEIGHT - gap - corner_len)],
    ]
    for pts in corners:
        draw.line([pts[0], pts[1]], fill=c, width=2)
        draw.line([pts[2], pts[3]], fill=c, width=2)

    # 水平扫描线（从上到下移动）
    scan_y = int((frame * 4) % HEIGHT)
    for dy in range(-2, 3):
        yy = scan_y + dy
        if 0 <= yy < HEIGHT:
            opacity = 1.0 - abs(dy) / 3.0
            sc = lerp_color(BG_COLOR, (0, 200, 160), opacity * 0.15)
            draw.line([(0, yy), (WIDTH, yy)], fill=sc, width=1)

    # 圆环十字准星
    cx, cy = CENTER
    cross_len = 15
    cross_gap = 25
    cc = lerp_color(CYAN_DIM, CYAN, 0.3 + 0.2 * math.sin(frame * 0.2))
    draw.line([(cx - cross_gap - cross_len, cy), (cx - cross_gap, cy)], fill=cc, width=1)
    draw.line([(cx + cross_gap, cy), (cx + cross_gap + cross_len, cy)], fill=cc, width=1)
    draw.line([(cx, cy - cross_gap - cross_len), (cx, cy - cross_gap)], fill=cc, width=1)
    draw.line([(cx, cy + cross_gap), (cx, cy + cross_gap + cross_len)], fill=cc, width=1)


# ============================================================
# 特效 3：能量脉冲波（从中心向外扩散）
# ============================================================

def draw_energy_pulse(draw, frame):
    """绘制从中心向外扩散的同心能量波"""
    cx, cy = CENTER
    max_r = 350.0
    pulse_interval = 25  # 每 25 帧产生一个新脉冲

    for pulse_birth in range(0, frame + 1, pulse_interval):
        age = frame - pulse_birth
        r = age * 8.0  # 扩散速度
        if r > max_r or r < 5:
            continue

        # 越远越淡
        fade = 1.0 - r / max_r
        if fade <= 0:
            continue

        color = lerp_color(BG_COLOR, (0, 220, 180), fade * 0.25)
        width = max(1, int(2 * fade))

        # 只绘制部分弧线，增加科幻感
        segments = 6
        for s in range(segments):
            angle_start = s * (360 / segments) + age * 2
            angle_end = angle_start + 40
            bbox = [cx - r, cy - r, cx + r, cy + r]
            draw.arc(bbox, angle_start, angle_end, fill=color, width=width)


# ============================================================
# 特效 4：轨道亮标（沿环快速运动的高亮小球）
# ============================================================

def draw_orbital_markers(draw, frame):
    """绘制沿环运动的发光标记球"""
    cx, cy = CENTER

    for ring_idx, (bright, dim, glow, radius, w, name) in enumerate(RING_DEFS):
        # 每个环上有 2 个标记球
        for marker_id in range(2):
            speed = (len(RING_DEFS) - ring_idx) * 0.12 + marker_id * 0.05
            angle = frame * speed + marker_id * math.pi

            mx = cx + radius * math.cos(angle)
            my = cy + radius * math.sin(angle)

            # 外圈光晕
            for gr in range(8, 1, -1):
                ga = 1.0 - gr / 8.0
                gc = lerp_color(BG_COLOR, glow, ga * 0.5)
                draw.ellipse([mx - gr, my - gr, mx + gr, my + gr], fill=gc)

            # 核心亮点
            draw.ellipse([mx - 3, my - 3, mx + 3, my + 3], fill=bright)
            draw.ellipse([mx - 1.5, my - 1.5, mx + 1.5, my + 1.5],
                         fill=(255, 255, 255))


# ============================================================
# 特效 5：环间电弧（环之间的能量连接线）
# ============================================================

def draw_electric_arcs(draw, frame):
    """绘制环之间的能量电弧"""
    cx, cy = CENTER
    rng = random.Random(frame // 3)  # 每 3 帧换一批电弧

    num_arcs = 3
    for _ in range(num_arcs):
        # 随机选两个相邻环
        r1_idx = rng.randint(0, len(RING_DEFS) - 2)
        r2_idx = r1_idx + 1

        r1 = RING_DEFS[r1_idx][3]
        r2 = RING_DEFS[r2_idx][3]

        angle = rng.uniform(0, 2 * math.pi)

        x1 = cx + r1 * math.cos(angle)
        y1 = cy + r1 * math.sin(angle)
        x2 = cx + r2 * math.cos(angle)
        y2 = cy + r2 * math.sin(angle)

        # 带弯曲的闪电线
        points = [(x1, y1)]
        steps = 6
        for s in range(1, steps):
            t = s / steps
            px = x1 + (x2 - x1) * t + rng.uniform(-8, 8)
            py = y1 + (y2 - y1) * t + rng.uniform(-8, 8)
            points.append((px, py))
        points.append((x2, y2))

        arc_color = lerp_color(
            RING_DEFS[r1_idx][2], RING_DEFS[r2_idx][2], 0.5
        )
        # 增加半透明感
        arc_color = lerp_color(BG_COLOR, arc_color, 0.6)

        draw.line(points, fill=arc_color, width=1)


# ============================================================
# 特效 6：增强粒子系统（带尾迹）
# ============================================================

def draw_particles_enhanced(draw, frame, count=60):
    """绘制带尾迹的能量粒子"""
    cx, cy = CENTER
    rng = random.Random(42)

    max_r = max(rd[3] for rd in RING_DEFS) + 60

    for i in range(count):
        # 粒子基础参数（固定种子保证连贯性）
        base_angle = rng.uniform(0, 2 * math.pi)
        base_r = rng.uniform(40, max_r)
        orbit_speed = rng.uniform(0.01, 0.04)
        radial_osc = rng.uniform(0, 10)  # 径向振荡幅度

        # 粒子颜色
        color_choices = [CYAN, GOLD_TEXT, (180, 80, 255), (255, 255, 255)]
        particle_color = color_choices[i % len(color_choices)]

        # 计算当前位置
        angle = base_angle + frame * orbit_speed
        r = base_r + radial_osc * math.sin(frame * 0.1 + i)

        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)

        # 尾迹（前 3 帧的位置）
        for t in range(3):
            trail_frame = frame - t - 1
            trail_angle = base_angle + trail_frame * orbit_speed
            trail_r = base_r + radial_osc * math.sin(trail_frame * 0.1 + i)
            tx = cx + trail_r * math.cos(trail_angle)
            ty = cy + trail_r * math.sin(trail_angle)

            fade = 0.3 * (1 - t / 3)
            tc = lerp_color(BG_COLOR, particle_color, fade)
            size = 0.5
            draw.ellipse([tx - size, ty - size, tx + size, ty + size], fill=tc)

        # 粒子本体
        size = rng.uniform(0.8, 1.8)
        pc = lerp_color(BG_COLOR, particle_color, 0.6)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=pc)


# ============================================================
# 核心环绘制（含辉光增强）
# ============================================================

def draw_ring_track_glow(draw, center, radius, color_dim):
    """绘制环的暗色轨道 + 微弱辉光"""
    cx, cy = center

    # 辉光层（更粗一点的暗色环）
    for glow_r in [radius - 2, radius - 1, radius, radius + 1, radius + 2]:
        num_pts = int(2 * math.pi * glow_r)
        fade = 1.0 - abs(glow_r - radius) / 3.0
        gc = lerp_color(BG_COLOR, color_dim, fade * 0.25)
        for i in range(num_pts):
            angle = 2 * math.pi * i / num_pts
            x = cx + glow_r * math.cos(angle)
            y = cy + glow_r * math.sin(angle)
            draw.ellipse([x - 0.5, y - 0.5, x + 0.5, y + 0.5], fill=gc)


def draw_arc_with_glow(draw, center, radius, start_angle, sweep_angle,
                       color_bright, color_dim, glow_color, ring_width):
    """绘制带流光尾迹和辉光的圆弧"""
    cx, cy = center
    num_segments = max(int(sweep_angle * radius / 2), 30)

    for i in range(num_segments):
        t = i / num_segments
        angle = start_angle + sweep_angle * t

        brightness = 1.0 - t * 0.85

        if brightness > 0.6:
            color = lerp_color(color_bright, color_dim, 1.0 - brightness)
        else:
            color = lerp_color(color_dim, BG_COLOR, 1.0 - brightness * 1.5)

        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)

        w = ring_width * brightness
        if w < 1.5:
            w = 1.5

        # 辉光层（更大更暗的外圈）
        if brightness > 0.3:
            glow_size = w * 2.5
            glow_c = lerp_color(BG_COLOR, glow_color, brightness * 0.2)
            draw.ellipse(
                [x - glow_size / 2, y - glow_size / 2,
                 x + glow_size / 2, y + glow_size / 2],
                fill=glow_c
            )

        # 弧线主体
        r = w / 2
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


# ============================================================
# 中心核心（增强版）
# ============================================================

def draw_core_enhanced(draw, center, frame):
    """绘制增强版中心核心：多层光晕 + 呼吸 + 交叉光芒"""
    cx, cy = center
    pulse = 0.7 + 0.3 * math.sin(frame * 0.3)

    # 最外层柔和光晕
    for r in range(35, 5, -1):
        fade = 1.0 - r / 35.0
        gc = lerp_color(BG_COLOR, CORE_GLOW, fade * 0.15 * pulse)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=gc)

    # 交叉光芒（十字星）
    ray_len = int(25 * pulse)
    ray_color = lerp_color(BG_COLOR, CORE_GLOW, 0.4 * pulse)
    for angle_offset in [0, math.pi / 4]:
        for deg in range(4):
            a = deg * math.pi / 2 + angle_offset + frame * 0.02
            for d in range(5, ray_len):
                fade = 1.0 - d / ray_len
                rx = cx + d * math.cos(a)
                ry = cy + d * math.sin(a)
                rc = lerp_color(BG_COLOR, CORE_GLOW, fade * 0.3)
                draw.ellipse([rx - 0.5, ry - 0.5, rx + 0.5, ry + 0.5], fill=rc)

    # 核心实心圆
    core_r = int(8 * pulse) + 5
    draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r],
                 fill=CORE_COLOR)

    # 最亮中心
    inner_r = max(core_r - 4, 3)
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                 fill=(255, 255, 240))


# ============================================================
# 文字标注
# ============================================================

def draw_text_labels(draw, center, ring_defs, frame):
    """绘制标题和标注"""
    cx, cy = center
    max_radius = max(rd[3] for rd in ring_defs) + 40

    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 13)
        font_label = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 11)
        font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 9)
    except OSError:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_label = font_title
        font_small = font_title

    # 标题闪烁效果
    title_alpha = 0.7 + 0.3 * math.sin(frame * 0.1)
    title_color = lerp_color(CYAN_DIM, CYAN, title_alpha)
    title = "◆ 魂 环 全 息 投 影 ◆"
    subtitle = "SOUL RING HOLOGRAM"
    bbox1 = draw.textbbox((0, 0), title, font=font_title)
    bbox2 = draw.textbbox((0, 0), subtitle, font=font_sub)
    tw1 = bbox1[2] - bbox1[0]
    tw2 = bbox2[2] - bbox2[0]
    draw.text((cx - tw1 // 2, 20), title, fill=title_color, font=font_title)
    draw.text((cx - tw2 // 2, 48), subtitle, fill=CYAN_DIM, font=font_sub)

    # 底部环型构成
    y_base = cy + max_radius + 15
    ring_text = "  ".join(
        f"第{i+1}环:{rd[5]}" for i, rd in enumerate(ring_defs)
    )
    bbox3 = draw.textbbox((0, 0), ring_text, font=font_sub)
    tw3 = bbox3[2] - bbox3[0]
    draw.text((cx - tw3 // 2, y_base), ring_text, fill=GOLD_TEXT, font=font_sub)

    # 差速旋转说明
    desc = "差速旋转 · 内圈快外圈慢 · Differential Rotation"
    bbox4 = draw.textbbox((0, 0), desc, font=font_label)
    tw4 = bbox4[2] - bbox4[0]
    draw.text((cx - tw4 // 2, y_base + 22), desc, fill=TEXT_DIM, font=font_label)

    # 左下角帧信息 HUD
    info = f"FRAME {frame:03d}/{TOTAL_FRAMES}  |  {len(ring_defs)} RINGS  |  DIFF-ROT"
    draw.text((25, HEIGHT - 30), info, fill=CYAN_DIM, font=font_small)

    # 右下角坐标 HUD
    coord = f"CX:{cx} CY:{cy} R:{max_radius}"
    bbox5 = draw.textbbox((0, 0), coord, font=font_small)
    draw.text((WIDTH - 25 - (bbox5[2] - bbox5[0]), HEIGHT - 30),
              coord, fill=CYAN_DIM, font=font_small)


# ============================================================
# 帧生成
# ============================================================

def generate_frame(frame_idx):
    """生成单帧"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Layer 0: 星空背景
    draw_starfield(draw, frame_idx)

    # Layer 1: HUD 边框
    draw_hud_frame(draw, frame_idx)

    # Layer 2: 能量脉冲波
    draw_energy_pulse(draw, frame_idx)

    # Layer 3: 粒子系统
    draw_particles_enhanced(draw, frame_idx)

    # Layer 4: 文字标注
    draw_text_labels(draw, CENTER, RING_DEFS, frame_idx)

    # Layer 5: 环轨道 + 辉光
    for ring_idx, (bright, dim, glow, radius, w, name) in enumerate(RING_DEFS):
        track_color = lerp_color(BG_COLOR, dim, 0.3)
        draw_ring_track_glow(draw, CENTER, radius, track_color)

    # Layer 6: 环间电弧
    draw_electric_arcs(draw, frame_idx)

    # Layer 7: 旋转流光弧
    for ring_idx, (bright, dim, glow, radius, w, name) in enumerate(RING_DEFS):
        speed = (len(RING_DEFS) - ring_idx) * 0.08
        rotation = frame_idx * speed
        sweep = math.pi * 1.4
        draw_arc_with_glow(draw, CENTER, radius, rotation, sweep,
                           bright, dim, glow, w)

    # Layer 8: 轨道亮标
    draw_orbital_markers(draw, frame_idx)

    # Layer 9: 中心核心
    draw_core_enhanced(draw, CENTER, frame_idx)

    # 后处理：轻微高斯模糊增加发光感
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))

    return img


# ============================================================
# 主程序
# ============================================================

def main():
    """生成魂环旋转动画 GIF"""
    import os

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "cli_soul_ring.gif"
    )

    print("🔮 生成魂环旋转动画 GIF v2（炫酷增强版）...")
    print(f"   尺寸: {WIDTH}x{HEIGHT}, 帧数: {TOTAL_FRAMES}, FPS: {FPS}")
    print(f"   特效: 星空 + HUD + 脉冲波 + 轨道亮标 + 电弧 + 粒子拖尾")

    frames = []
    for i in range(TOTAL_FRAMES):
        frame = generate_frame(i)
        frames.append(frame)
        pct = (i + 1) / TOTAL_FRAMES * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"\r   [{bar}] {pct:5.1f}% ({i+1}/{TOTAL_FRAMES})", end="",
              flush=True)

    print(f"\n   保存 GIF → {output_path}")

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=True,
    )

    file_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"   ✅ 完成! 大小: {file_size:.2f} MB")


if __name__ == "__main__":
    main()
