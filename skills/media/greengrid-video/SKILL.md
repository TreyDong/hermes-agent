---
name: greengrid-video
description: 易电通GreenGrid官网介绍视频制作流水线——截图→TTS→字幕→ffmpeg合成→Discord上传
tags: [video, greengrid, ffmpeg, tts, screenshots]
---

# 易电通官网介绍视频制作流水线

## 目标
- 时长：~120秒（2分钟）
- 图片：35张官网截图，硬切过渡，无Ken Burns动效
- 配音：MiniMax TTS，精品男声（male-qn-jingying-jingpin）
- 字幕：ASS格式，底部居中，白字+黑色描边，字幕与配音精确同步
- BGM：待定（可后加）
- 输出：/tmp/video_output/greengrid_intro_final.mp4

## Step 1：TTS配音生成

### 1a. 话术脚本（已写好，路径：/tmp/video_output/greengrid_tts_script.txt）

```
欢迎使用易电通EC绿色电力平台，我们是您的跨境电力设备贸易伙伴。

易电通聚焦智能电网与新能源领域，覆盖电力变压器、开关设备、电线电缆、光伏组件、储能系统等核心品类，为全球买家与卖家搭建高效的撮合通道。

平台汇聚海量真实供应商，提供按品类、按地区、按认证类型的多维筛选，轻轻一点即可快速锁定目标货源。

我们深知电力设备采购决策链长、风险高，因此重磅推出资信评级体系。每一笔交易都有信用背书，买家放心下单，卖家安心接单。

采购过程中最耗时的环节是什么？比价。易电通一键发布询价，系统自动推送至匹配供应商，批量报价对比清晰呈现，大幅缩短决策周期。

物流、通关、收汇，这是跨境贸易的三座大山。平台提供一站式服务，从出厂到交付，全程可视化追踪，省心省力。

如果您是制造厂商，易电通不仅是卖货渠道，更是品牌出海的加速器。平台提供数据分析、流量扶持、运营指导，帮助厂商快速建立全球影响力。

如果是海外采购商，我们提供资金融通方案，支持信用证、保函等多种支付方式，解决您的资金周转压力。

注册只需三分钟，完善企业资质后即可解锁全部功能。新用户首单免收服务费，还有专属客服全程跟进。

登录易电通，进入管理后台。您可以在此管理询价记录、跟踪订单状态、查看物流动态、处理收汇结算。所有数据一目了然。

易电通，让跨境电力贸易更简单。立即注册，开启您的全球电力贸易新篇章。
```

### 1b. 生成TTS（MiniMax）

```bash
mmx tts \
  --api-key "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  --model "speech-02-hd" \
  --timber-wt "male-qn-jingying-jingpin" \
  --input "/tmp/video_output/greengrid_tts_script.txt" \
  --output "/tmp/video_output/greengrid_tts.mp3"
```

### 1c. 获取精确时长

```bash
ffprobe -v error -show_entries format=duration \
  -of csv=p=0 /tmp/video_output/greengrid_tts.mp3
```

记下这个时长 `DURATION`，用于Step 3计算时间轴。

---

## Step 2：截图（35张）

目标：ec.greengrid.com.cn 全站关键页面

用 `agent-browser` 截图，截图后用 ffmpeg 统一处理为 1280×720：

```bash
# 统一尺寸
ffmpeg -y -i /tmp/screenshot_N.png \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black" \
  /tmp/video_output/screenshots/screenshot_N_720p.png
```

**35张截图清单**：

首页区域：
1. 首页全屏Banner（Hero）
2. 首页产品分类入口区
3. 首页解决方案展示区
4. 首页核心业务板块（商机匹配/资信评级等）
5. 首页合作模式介绍
6. 顶部导航栏
7. 底部Footer

产品分类页：
8. 产品分类页全貌
9. 电力变压器分类
10. 开关设备分类
11. 电线电缆分类
12. 光伏组件分类
13. 储能系统分类
14. 分类筛选条件区
15. 分类搜索结果页

解决方案页：
16. 解决方案页
17. 供应商解决方案
18. 采购商解决方案
19. 物流服务介绍
20. 通关服务介绍
21. 支付收汇服务

会员/注册：
22. 注册页全貌
23. 注册页填写表单
24. 登录页
25. 企业认证引导页

询价/订单：
26. 发布询价页
27. 询价表单填写
28. 询价记录列表
29. 订单管理页

后台管理：
30. 管理后台概览
31. 询价管理
32. 订单跟踪
33. 物流追踪
34. 收汇结算
35. 客服支持页

---

## Step 3：字幕ASS文件生成

**关键：字幕放底部居中，不是右上角！**

根据 TTS 实际时长 `DURATION`，计算时间轴：
- 每张图时长 = `DURATION / 35` 秒
- 用 Python 生成 ASS 文件，按时间轴分配字幕行

ASS模板（底部居中，白字+黑边）：
```
[Script Info]
Title: 易电通官网介绍
ScriptType: v4.00+
PlayDepth: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,2,10,10,30,1

[Events]
Format: Layer,Start,End,Style,Text
Dialogue: 0,0:00:00.00,0:00:03.40,*Default,欢迎使用易电通EC绿色电力平台...
...
```

Alignment=2 表示底部居中。

---

## Step 4：ffmpeg视频合成

### 4a. 生成各片段（静态图 + ASS字幕）

每张图生成一个独立片段，时长 = `DURATION/35` 秒：

```bash
for i in $(seq 1 35); do
  IMG="/tmp/video_output/screenshots/screenshot_${i}_720p.png"
  ASS="/tmp/video_output/subtitle_${i}.ass"
  OUT="/tmp/video_output/segments/seg_${i}.mp4"
  
  # 生成单片段（静态图 + 字幕）
  ffmpeg -y -loop 1 -i "$IMG" -filter_complex "
    [0:v]trim=0:$PER_SCENE,setpts=PTS-STARTPTS,
    ass='$ASS':fontsdir=/usr/share/fonts/truetype/dejavu,
    scale=1280:720:force_original_aspect_ratio=decrease,
    pad=1280:720:(ow-iw)/2:(oh-ih)/2:black
  " -t $PER_SCENE -r 25 -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -an "$OUT"
done
```

### 4b. 合并所有片段

```bash
# 生成 concat 文件
for i in $(seq 1 35); do
  echo "file '/tmp/video_output/segments/seg_${i}.mp4'" >> /tmp/video_output/segments/concat.txt
done

# 合并视频（无音）
ffmpeg -y -f concat -safe 0 -i /tmp/video_output/segments/concat.txt \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
  /tmp/video_output/greengrid_video_noaudio.mp4
```

### 4c. 合并视频 + 音频

```bash
ffmpeg -y -i /tmp/video_output/greengrid_video_noaudio.mp4 \
  -i /tmp/video_output/greengrid_tts.mp3 \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -shortest \
  /tmp/video_output/greengrid_intro_final.mp4
```

---

## Step 5：Discord上传

```bash
~/bin/discord-cli msg "$(date +%Y-%m-%d) 易电通官网介绍视频" \
  --thread "$CURRENT_THREAD_ID"

# 直接发文件
curl -F "file=@/tmp/video_output/greengrid_intro_final.mp4" \
  -F "thread_id=$CURRENT_THREAD_ID" \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  "https://discord.com/api/v10/channels/$CHANNEL_ID/messages"
```

---

## 已知问题 & 修复记录

- ❌ 之前字幕放右上角（错误）→ 修复：改用底部居中（Alignment=2）
- ❌ 之前Ken Burns动效（画面移动） → 修复：静态图硬切，无动效
- ❌ 之前4张图太少 → 修复：35张图
- ❌ 之前时长太短（~25秒）→ 修复：120秒完整话术
- ✓ 音色：male-qn-jingying-jingpin（精品男声）已验证OK
