import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// ─── 速报模板：单图素材 + 15秒短视频 ────────────────────────────────────────
// 适合突发新闻/产品发布，配一张截图，区别于 YokoShort(数据卡片) 和 EditorialShort(杂志风)

export interface BreakingFlashProps extends Record<string, unknown> {
  // 静态文件名（放 remotion/public/），留空时显示占位卡片
  image_file: string;
  // 顶部徽章，如 "速报"
  badge: string;
  // 3 条主标题，逐行显示
  headline_lines: [string, string, string];
  // 底部滚动条文字
  ticker_text: string;
  // 来源署名
  source: string;
  // 口播文案（备用，不上屏）
  voiceover: string;
}

export const BREAKING_FLASH_DURATION = 450; // 15s @ 30fps

const FONT = '"Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif';

const BG = "#080C10";
const GREEN = "#07C160"; // WeChat green
const WHITE = "#FFFFFF";
const DIM = "#8A9BB0";
const CARD_BG = "#111820";

// ─── 背景：深色 + 细点阵纹 ─────────────────────────────────────────────────
const DotBackground: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: BG}}>
    {/* 细点阵：用 radial-gradient 模拟 */}
    <AbsoluteFill
      style={{
        backgroundImage: `radial-gradient(circle, ${GREEN}18 1px, transparent 1px)`,
        backgroundSize: "48px 48px",
        opacity: 0.35,
      }}
    />
    {/* 顶部光晕 */}
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse 80% 40% at 50% 0%, ${GREEN}12, transparent 60%)`,
      }}
    />
  </AbsoluteFill>
);

// ─── 图片卡片：绿色发光边框 + scale-in 动效 ────────────────────────────────
const ImageCard: React.FC<{at: number; src: string}> = ({at, src}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at, fps, config: {damping: 160, stiffness: 80}});
  const scale = interpolate(s, [0, 1], [0.88, 1]);
  const opacity = interpolate(s, [0, 1], [0, 1]);
  // 扫描线扫过后发光强度
  const scanFrame = Math.max(0, frame - at - 15);
  const glowPulse = interpolate(
    Math.min(scanFrame, 30),
    [0, 15, 30],
    [0, 1, 0.6],
    {extrapolateRight: "clamp"},
  );
  const glow = `0 0 ${40 + glowPulse * 40}px ${GREEN}${Math.round(glowPulse * 60 + 24).toString(16)}`;

  return (
    <div
      style={{
        opacity,
        transform: `scale(${scale})`,
        borderRadius: 28,
        overflow: "hidden",
        border: `3px solid ${GREEN}${Math.round(40 + glowPulse * 100).toString(16)}`,
        boxShadow: glow,
        background: CARD_BG,
      }}
    >
      <Img
        src={src}
        style={{
          width: "100%",
          display: "block",
          objectFit: "cover",
        }}
      />
    </div>
  );
};

const PlaceholderCard: React.FC<{at: number}> = ({at}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at, fps, config: {damping: 160, stiffness: 80}});
  const scale = interpolate(s, [0, 1], [0.88, 1]);
  const opacity = interpolate(s, [0, 1], [0, 1]);

  return (
    <div
      style={{
        opacity,
        transform: `scale(${scale})`,
        borderRadius: 28,
        overflow: "hidden",
        border: `3px solid ${GREEN}88`,
        boxShadow: `0 0 50px ${GREEN}33`,
        background: CARD_BG,
        minHeight: 520,
        padding: 44,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: 26,
      }}
    >
      <div style={{color: GREEN, fontSize: 34, fontWeight: 900}}>
        PUBLIC SAMPLE
      </div>
      <div
        style={{
          color: WHITE,
          fontSize: 64,
          fontWeight: 850,
          lineHeight: 1.15,
        }}
      >
        把 AI 新闻
        <br />
        变成短视频选题
      </div>
      <div style={{color: DIM, fontSize: 32, lineHeight: 1.38, fontWeight: 600}}>
        替换 remotion/breaking-flash.json 或放入自己的截图素材。
      </div>
    </div>
  );
};

// ─── 单行标题：从下方滑入 ──────────────────────────────────────────────────
const HeadlineLine: React.FC<{
  at: number;
  text: string;
  size: number;
  color?: string;
}> = ({at, text, size, color = WHITE}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at, fps, config: {damping: 180, stiffness: 120}});
  const opacity = interpolate(s, [0, 1], [0, 1]);
  const ty = interpolate(s, [0, 1], [40, 0]);
  return (
    <div
      style={{
        opacity,
        transform: `translateY(${ty}px)`,
        color,
        fontSize: size,
        fontWeight: 800,
        lineHeight: 1.28,
        letterSpacing: "-0.01em",
      }}
    >
      {text}
    </div>
  );
};

// ─── 底部速报条：从下方滑入 ────────────────────────────────────────────────
const TickerBar: React.FC<{at: number; text: string; source: string}> = ({
  at,
  text,
  source,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at, fps, config: {damping: 200}});
  const ty = interpolate(s, [0, 1], [80, 0]);
  const opacity = interpolate(s, [0, 1], [0, 1]);
  return (
    <div
      style={{
        opacity,
        transform: `translateY(${ty}px)`,
        background: `linear-gradient(90deg, ${GREEN}EE, ${GREEN}BB)`,
        padding: "22px 48px",
        borderRadius: 20,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <div
        style={{
          color: "#000",
          fontSize: 32,
          fontWeight: 700,
          lineHeight: 1.35,
        }}
      >
        {text}
      </div>
      <div style={{color: "#00000066", fontSize: 26, fontWeight: 500}}>
        {source}
      </div>
    </div>
  );
};

// ─── 主组件 ────────────────────────────────────────────────────────────────
export const BreakingFlash: React.FC<BreakingFlashProps> = (props) => {
  const {
    image_file,
    badge,
    headline_lines,
    ticker_text,
    source,
  } = props;

  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // 徽章动效
  const badgeS = spring({frame, fps, config: {damping: 180}});
  const badgeTx = interpolate(badgeS, [0, 1], [-160, 0]);
  const badgeOp = interpolate(badgeS, [0, 1], [0, 1]);

  return (
    <AbsoluteFill style={{fontFamily: FONT}}>
      <DotBackground />

      {/* ─ 全部内容纵向布局 ─ */}
      <AbsoluteFill
        style={{
          flexDirection: "column",
          padding: "80px 60px 200px 60px",
          gap: 0,
        }}
      >
        {/* 速报徽章 */}
        <div
          style={{
            opacity: badgeOp,
            transform: `translateX(${badgeTx}px)`,
            alignSelf: "flex-start",
            background: GREEN,
            color: "#000",
            fontSize: 32,
            fontWeight: 800,
            padding: "10px 28px",
            borderRadius: 40,
            letterSpacing: "0.06em",
            marginBottom: 48,
          }}
        >
          {badge}
        </div>

        {/* 图片卡片区 */}
        <div style={{marginBottom: 60}}>
          {image_file ? (
            <ImageCard at={8} src={staticFile(image_file)} />
          ) : (
            <PlaceholderCard at={8} />
          )}
        </div>

        {/* 标题区：3 行逐步显示 */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "flex-start",
            gap: 24,
          }}
        >
          <HeadlineLine at={90} text={headline_lines[0]} size={68} />
          <HeadlineLine
            at={135}
            text={headline_lines[1]}
            size={58}
            color={GREEN}
          />
          <HeadlineLine at={180} text={headline_lines[2]} size={52} color={DIM} />
        </div>

        {/* 底部速报条 */}
        <TickerBar at={280} text={ticker_text} source={source} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
