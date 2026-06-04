import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import {YokoShortProps} from "./YokoShort";

// 编辑杂志风：米白纸面 + 宋体超大标题 + 朱红 accent + 强版式
const PAPER = "#f3efe3";
const INK = "#1a1a1a";
const RED = "#c8102e";
const GREY = "#6f6a5d";

const FONT_SERIF = '"SimSun", "Songti SC", "Source Han Serif SC", "STSong", serif';
const FONT_NUM = 'Georgia, "Times New Roman", serif';
const FONT_MONO = '"Cascadia Mono", "Consolas", monospace';

const AT_TITLE = 0;
const AT_LINE = 12;
const AT_DATA = 20;
const AT_POINT_BASE = 34;
const AT_POINT_STEP = 14;

export const calcEditorialFrames = (p: YokoShortProps, fps = 30): number => {
  const n = p.key_points?.length ?? 0;
  const buildEnd = AT_POINT_BASE + n * AT_POINT_STEP + 30;
  return buildEnd + 12 * fps;
};

const FadeIn: React.FC<{at: number; children: React.ReactNode}> = ({
  at,
  children,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at, fps, config: {damping: 200}});
  const opacity = interpolate(s, [0, 1], [0, 1]);
  const ty = interpolate(s, [0, 1], [24, 0]);
  return (
    <div style={{opacity, transform: `translateY(${ty}px)`}}>{children}</div>
  );
};

// 分隔线从左展开（高影响力动效）
const LineReveal: React.FC<{at: number; color: string; height: number}> = ({
  at,
  color,
  height,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at, fps, config: {damping: 200}});
  const w = interpolate(s, [0, 1], [0, 100]);
  return <div style={{height, background: color, width: `${w}%`}} />;
};

export const EditorialShort: React.FC<YokoShortProps> = (props) => {
  const {title_caption, data_points, key_points} = props;
  const hasData = (data_points?.length ?? 0) > 0;

  return (
    <AbsoluteFill style={{backgroundColor: PAPER, fontFamily: FONT_SERIF}}>
      {/* 装饰：右上超大引号 */}
      <div
        style={{
          position: "absolute",
          top: -110,
          right: 20,
          fontSize: 460,
          lineHeight: 1,
          color: RED,
          opacity: 0.08,
          fontFamily: FONT_NUM,
          fontWeight: 700,
        }}
      >
        ”
      </div>

      {/* 内容区：垂直居中、左对齐版式 */}
      <AbsoluteFill
        style={{
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "flex-start",
          padding: "0 76px",
        }}
      >
        {/* 标题 */}
        <FadeIn at={AT_TITLE}>
          <div
            style={{
              color: INK,
              fontSize: 78,
              fontWeight: 700,
              lineHeight: 1.32,
            }}
          >
            {title_caption}
          </div>
        </FadeIn>

        {/* 朱红分隔线 */}
        <div style={{width: "100%", marginTop: 40, marginBottom: 40}}>
          <LineReveal at={AT_LINE} color={RED} height={6} />
        </div>

        {/* 数据：大衬线数字 */}
        {hasData && (
          <FadeIn at={AT_DATA}>
            <div style={{display: "flex", gap: 70, flexWrap: "wrap"}}>
              {data_points.slice(0, 3).map((dp, i) => (
                <div key={i}>
                  <div
                    style={{
                      fontFamily: FONT_NUM,
                      fontSize: 104,
                      fontWeight: 700,
                      color: RED,
                      lineHeight: 1,
                    }}
                  >
                    {dp.value}
                  </div>
                  <div style={{color: GREY, fontSize: 30, marginTop: 12}}>
                    {dp.label}
                  </div>
                </div>
              ))}
            </div>
          </FadeIn>
        )}

        {/* 要点：编号列表 + 细分隔线 */}
        <div
          style={{
            marginTop: 50,
            display: "flex",
            flexDirection: "column",
            gap: 30,
            width: "100%",
          }}
        >
          {key_points.map((kp, i) => (
            <FadeIn key={i} at={AT_POINT_BASE + i * AT_POINT_STEP}>
              <div
                style={{
                  display: "flex",
                  gap: 30,
                  alignItems: "baseline",
                  borderBottom: `1px solid ${INK}22`,
                  paddingBottom: 26,
                }}
              >
                <div
                  style={{
                    fontFamily: FONT_NUM,
                    fontSize: 48,
                    fontWeight: 700,
                    color: RED,
                    flexShrink: 0,
                  }}
                >
                  {String(i + 1).padStart(2, "0")}
                </div>
                <div
                  style={{
                    color: INK,
                    fontSize: 44,
                    fontWeight: 600,
                    lineHeight: 1.42,
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
