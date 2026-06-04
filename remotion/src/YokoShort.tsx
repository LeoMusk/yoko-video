import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

export interface DataPoint {
  value: string;
  label: string;
}

export interface YokoShortProps extends Record<string, unknown> {
  title_caption: string;
  hook: string;
  data_points: DataPoint[];
  key_points: string[];
  yoko_take: string;
  cta: string;
  voiceover: string;
  visual_cues: string[];
  duration_sec: number;
  meta: {
    title: string;
    source: string;
    category: string;
    url: string;
    final: number | null;
  };
}

const FONT_CN = '"Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif';
const FONT_MONO = '"Cascadia Mono", "Consolas", "Courier New", monospace';
const BG = "#060a14";
const CYAN = "#22d3ee";
const GREEN = "#4ade80";
const WHITE = "#f1f5f9";
const SUB = "#94a3b8";

// 各元素渐进出现的帧偏移
const AT_TITLE = 0;
const AT_DATA = 14;
const AT_POINT_BASE = 32;
const AT_POINT_STEP = 16;

// 时长 = 元素全部出现 + 保持供阅读（无字幕/无音频阶段）。接 TTS 后改为音频时长。
export const calcDurationInFrames = (p: YokoShortProps, fps = 30): number => {
  const n = p.key_points?.length ?? 0;
  const buildEnd = AT_POINT_BASE + n * AT_POINT_STEP + 30;
  return buildEnd + 12 * fps;
};

// 动态科技背景：网格 + 中心光晕 + 上浮粒子
const TechBackground: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const particles = Array.from({length: 16}, (_, i) => {
    const x = (i * 137.5) % width;
    const speed = 0.4 + (i % 5) * 0.15;
    const y = height - (((frame * speed) + i * 90) % (height + 120));
    const size = 3 + (i % 3) * 3;
    const op = 0.12 + (i % 4) * 0.06;
    return {x, y, size, op};
  });
  return (
    <AbsoluteFill style={{backgroundColor: BG}}>
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${CYAN}1a 1px, transparent 1px), linear-gradient(90deg, ${CYAN}1a 1px, transparent 1px)`,
          backgroundSize: "84px 84px",
          opacity: 0.4,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 50%, ${CYAN}1f, transparent 58%)`,
        }}
      />
      {particles.map((p, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: p.x,
            top: p.y,
            width: p.size,
            height: p.size,
            borderRadius: "50%",
            background: CYAN,
            opacity: p.op,
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

// 渐进淡入（出现后保留）
const FadeIn: React.FC<{at: number; children: React.ReactNode}> = ({
  at,
  children,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at, fps, config: {damping: 200}});
  const opacity = interpolate(s, [0, 1], [0, 1]);
  const ty = interpolate(s, [0, 1], [28, 0]);
  return (
    <div style={{opacity, transform: `translateY(${ty}px)`}}>{children}</div>
  );
};

export const YokoShort: React.FC<YokoShortProps> = (props) => {
  const {title_caption, data_points, key_points} = props;
  const hasData = (data_points?.length ?? 0) > 0;

  return (
    <AbsoluteFill style={{backgroundColor: BG, fontFamily: FONT_CN}}>
      <TechBackground />

      {/* 核心内容区：垂直居中，无顶部分类 / 无底部字幕 / 无品牌 */}
      <AbsoluteFill
        style={{
          flexDirection: "column",
          justifyContent: "center",
          padding: "0 64px",
          gap: 46,
        }}
      >
        {/* 标题 */}
        <FadeIn at={AT_TITLE}>
          <div
            style={{
              color: WHITE,
              fontSize: 64,
              fontWeight: 800,
              lineHeight: 1.28,
            }}
          >
            {title_caption}
          </div>
        </FadeIn>

        {/* 数据 */}
        {hasData && (
          <FadeIn at={AT_DATA}>
            <div
              style={{
                display: "flex",
                gap: 54,
                flexWrap: "wrap",
                paddingBottom: 40,
                borderBottom: `2px solid ${CYAN}26`,
              }}
            >
              {data_points.slice(0, 3).map((dp, i) => (
                <div key={i} style={{textAlign: "left"}}>
                  <div
                    style={{
                      fontFamily: FONT_MONO,
                      fontSize: 104,
                      fontWeight: 800,
                      color: GREEN,
                      lineHeight: 1,
                      textShadow: `0 0 40px ${GREEN}44`,
                    }}
                  >
                    {dp.value}
                  </div>
                  <div style={{color: SUB, fontSize: 32, marginTop: 14}}>
                    {dp.label}
                  </div>
                </div>
              ))}
            </div>
          </FadeIn>
        )}

        {/* 要点：同屏堆叠，逐条淡入保留 */}
        <div style={{display: "flex", flexDirection: "column", gap: 30}}>
          {key_points.map((kp, i) => (
            <FadeIn key={i} at={AT_POINT_BASE + i * AT_POINT_STEP}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 32,
                  background: "rgba(34,211,238,0.06)",
                  borderLeft: `7px solid ${CYAN}`,
                  borderRadius: 18,
                  padding: "32px 38px",
                }}
              >
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 60,
                    fontWeight: 800,
                    color: CYAN,
                    flexShrink: 0,
                  }}
                >
                  {String(i + 1).padStart(2, "0")}
                </div>
                <div
                  style={{
                    color: WHITE,
                    fontSize: 44,
                    fontWeight: 600,
                    lineHeight: 1.4,
                  }}
                >
                  {kp}
                </div>
              </div>
            </FadeIn>
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
