import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FONT_CN =
  '"Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif';
const FONT_MONO = '"Cascadia Mono", "Consolas", "Courier New", monospace';

const BG = "#07070D";
const INK = "#F5F6FA";
const DIM = "#B6BCD0";
const MUTE = "#7D859B";
const ACCENT = "#A78BFF";
const CYAN = "#00E5FF";
const PINK = "#FF3D8B";
const UP = "#00FFA3";
const LINE = "rgba(255,255,255,0.14)";

const facts = [
  {
    label: "Fast 模式",
    value: "↓66%",
    sub: "$30/$150 -> $10/$50",
    color: UP,
  },
  {
    label: "输出速度",
    value: "2.5x",
    sub: "Fast mode",
    color: CYAN,
  },
  {
    label: "常规价格",
    value: "$5/$25",
    sub: "每百万 token",
    color: ACCENT,
  },
];

const bench = [
  {name: "SWE-bench Verified", value: "88.6", delta: "+1.0"},
  {name: "SWE-bench Pro", value: "69.2", delta: "+4.9"},
  {name: "Terminal-Bench 2.1", value: "74.6", delta: "+8.5"},
];

const sources = "Anthropic / VentureBeat / GitHub · 2026-05-28";

export const OPUS48_DURATION = 450;

const appear = (frame: number, at: number, fps: number) =>
  spring({frame: frame - at, fps, config: {damping: 190, mass: 0.8}});

const FadeUp: React.FC<{
  at: number;
  children: React.ReactNode;
  distance?: number;
}> = ({at, children, distance = 34}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = appear(frame, at, fps);
  return (
    <div
      style={{
        opacity: interpolate(s, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(s, [0, 1], [distance, 0])}px)`,
      }}
    >
      {children}
    </div>
  );
};

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const gridShift = frame * 0.35;
  const pulse = Math.sin(frame / 24) * 0.5 + 0.5;
  return (
    <AbsoluteFill style={{backgroundColor: BG}}>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 50% 35%, rgba(124,92,255,0.25), transparent 44%), radial-gradient(circle at 72% 62%, rgba(0,229,255,0.12), transparent 32%)",
          opacity: 0.95,
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(124,92,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(124,92,255,0.08) 1px, transparent 1px)",
          backgroundSize: "72px 72px",
          backgroundPosition: `0 ${gridShift}px`,
          opacity: 0.42,
        }}
      />
      <AbsoluteFill
        style={{
          boxShadow: "inset 0 0 260px rgba(0,0,0,0.75)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(115deg, transparent 0%, rgba(255,255,255,0.06) 48%, transparent 58%)",
          transform: `translateX(${interpolate(frame, [0, OPUS48_DURATION], [-900, 900])}px)`,
          opacity: 0.26 + pulse * 0.1,
        }}
      />
    </AbsoluteFill>
  );
};

const ProductSquare: React.FC = () => {
  const frame = useCurrentFrame();
  const rotate = frame * 1.8;
  const glow = Math.sin(frame / 13) * 0.5 + 0.5;
  return (
    <div
      style={{
        position: "relative",
        width: 500,
        height: 500,
        borderRadius: 46,
        padding: 7,
        background: `conic-gradient(from ${rotate}deg, ${ACCENT}, ${CYAN}, ${PINK}, ${ACCENT})`,
        boxShadow: `0 28px 110px rgba(124,92,255,${0.24 + glow * 0.12})`,
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          borderRadius: 39,
          background: "linear-gradient(145deg, #1A0F2E, #080812 72%)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          border: `1px solid ${LINE}`,
        }}
      >
        <div
          style={{
            width: 178,
            height: 178,
            borderRadius: 38,
            background: "linear-gradient(135deg, #D97757, #B85C3E)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            fontFamily: FONT_MONO,
            fontSize: 86,
            fontWeight: 900,
            boxShadow:
              "0 28px 86px rgba(217,119,87,0.38), inset 0 3px 0 rgba(255,255,255,0.22)",
          }}
        >
          ✱
        </div>
        <div
          style={{
            color: INK,
            fontSize: 44,
            fontWeight: 800,
            marginTop: 38,
          }}
        >
          Claude Opus
        </div>
        <div
          style={{
            color: DIM,
            fontFamily: FONT_MONO,
            fontSize: 35,
            marginTop: 10,
          }}
        >
          v4.8 · NOW LIVE
        </div>
      </div>
    </div>
  );
};

const FactCard: React.FC<{
  item: (typeof facts)[number];
  index: number;
}> = ({item, index}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = appear(frame, 96 + index * 8, fps);
  return (
    <div
      style={{
        opacity: interpolate(s, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(s, [0, 1], [44, 0])}px)`,
        background: "rgba(19,24,38,0.78)",
        border: `1px solid ${LINE}`,
        borderRadius: 28,
        width: 304,
        height: 210,
        padding: "25px 22px",
        textAlign: "center",
      }}
    >
      <div
        style={{
          color: MUTE,
          fontSize: 27,
          letterSpacing: 0,
          fontWeight: 600,
        }}
      >
        {item.label}
      </div>
      <div
        style={{
          color: item.color,
          fontFamily: FONT_MONO,
          fontSize: 66,
          fontWeight: 900,
          lineHeight: 1,
          marginTop: 18,
        }}
      >
        {item.value}
      </div>
      <div
        style={{
          color: DIM,
          fontFamily: FONT_MONO,
          fontSize: 24,
          marginTop: 15,
          whiteSpace: "pre-wrap",
        }}
      >
        {item.sub}
      </div>
    </div>
  );
};

const BenchCard: React.FC<{
  item: (typeof bench)[number];
  index: number;
}> = ({item, index}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = appear(frame, 224 + index * 9, fps);
  return (
    <div
      style={{
        opacity: interpolate(s, [0, 1], [0, 1]),
        transform: `translateX(${interpolate(s, [0, 1], [50, 0])}px)`,
        height: 146,
        borderRadius: 26,
        background:
          index === 0
            ? "linear-gradient(135deg, rgba(124,92,255,0.24), rgba(124,92,255,0.06))"
            : "rgba(19,24,38,0.7)",
        border: `1px solid ${index === 0 ? "rgba(167,139,255,0.6)" : LINE}`,
        padding: "22px 30px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}
    >
      <div>
        <div style={{color: INK, fontSize: 35, fontWeight: 750}}>
          {item.name}
        </div>
        <div
          style={{
            color: MUTE,
            fontFamily: FONT_MONO,
            fontSize: 24,
            marginTop: 10,
          }}
        >
          vs Opus 4.7
        </div>
      </div>
      <div style={{textAlign: "right"}}>
        <div
          style={{
            color: index === 0 ? ACCENT : INK,
            fontFamily: FONT_MONO,
            fontSize: 60,
            fontWeight: 900,
            lineHeight: 1,
          }}
        >
          {item.value}
        </div>
        <div
          style={{
            color: UP,
            fontFamily: FONT_MONO,
            fontSize: 28,
            fontWeight: 800,
            marginTop: 8,
          }}
        >
          ▲ {item.delta}
        </div>
      </div>
    </div>
  );
};

const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const width = interpolate(frame, [0, OPUS48_DURATION - 1], [0, 100], {
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: 72,
        bottom: 70,
        width: 936,
        height: 7,
        borderRadius: 99,
        background: "rgba(255,255,255,0.12)",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: `${width}%`,
          height: "100%",
          background: `linear-gradient(90deg, ${ACCENT}, ${CYAN})`,
        }}
      />
    </div>
  );
};

export const Opus48Launch: React.FC = () => {
  const frame = useCurrentFrame();
  const scene2 = frame >= 88;
  const scene3 = frame >= 210;
  const final = frame >= 338;

  const titleOpacity = final ? 0.18 : scene3 ? 0 : 1;
  const productOpacity = scene2 ? (scene3 ? 0 : 1) : 1;
  const factsOpacity = scene2 && !scene3 ? 1 : 0;
  const benchOpacity = scene3 && !final ? 1 : 0;

  return (
    <AbsoluteFill style={{fontFamily: FONT_CN, color: INK}}>
      <Background />

      <AbsoluteFill style={{padding: "0 72px"}}>
        <div
          style={{
            position: "absolute",
            top: 116,
            left: 72,
            right: 72,
            opacity: titleOpacity,
          }}
        >
          <FadeUp at={0}>
            <div
              style={{
                color: MUTE,
                fontSize: 30,
                fontWeight: 650,
                letterSpacing: 0,
              }}
            >
              🔴 重磅发布 · 2026-05-28
            </div>
          </FadeUp>
          <FadeUp at={8}>
            <div
              style={{
                color: INK,
                fontSize: 86,
                fontWeight: 900,
                lineHeight: 1.08,
                marginTop: 24,
                textShadow: "0 0 42px rgba(124,92,255,0.35)",
              }}
            >
              Claude Opus 4.8
              <br />
              刚刚上线
            </div>
          </FadeUp>
          <FadeUp at={18}>
            <div
              style={{
                color: DIM,
                fontSize: 38,
                lineHeight: 1.3,
                marginTop: 22,
              }}
            >
              不是“换皮更新”，而是把开发者最疼的价格和长任务稳定性一起补了。
            </div>
          </FadeUp>
        </div>

        <div
          style={{
            position: "absolute",
            top: 600,
            left: 290,
            opacity: productOpacity,
            transform: `scale(${scene2 ? 0.78 : 1}) translateY(${scene2 ? -38 : 0}px)`,
          }}
        >
          <FadeUp at={28}>
            <ProductSquare />
          </FadeUp>
        </div>

        <div
          style={{
            position: "absolute",
            top: 1080,
            left: 48,
            right: 48,
            display: "flex",
            gap: 18,
            opacity: factsOpacity,
          }}
        >
          {facts.map((item, index) => (
            <FactCard key={item.label} item={item} index={index} />
          ))}
        </div>

        <div
          style={{
            position: "absolute",
            top: 438,
            left: 72,
            right: 72,
            opacity: benchOpacity,
          }}
        >
          <FadeUp at={210}>
            <div
              style={{
                color: INK,
                fontSize: 58,
                fontWeight: 880,
                lineHeight: 1.12,
                marginBottom: 30,
              }}
            >
              性能不是暴跳，
              <br />
              但关键榜单都在涨
            </div>
          </FadeUp>
          <div style={{display: "flex", flexDirection: "column", gap: 22}}>
            {bench.map((item, index) => (
              <BenchCard key={item.name} item={item} index={index} />
            ))}
          </div>
          <FadeUp at={262}>
            <div
              style={{
                color: DIM,
                fontSize: 34,
                lineHeight: 1.35,
                marginTop: 34,
              }}
            >
              GitHub Copilot 也已经接入，但企业/商业用户需要管理员开启策略。
            </div>
          </FadeUp>
        </div>

        {final && (
          <div
            style={{
              position: "absolute",
              top: 506,
              left: 72,
              right: 72,
            }}
          >
            <FadeUp at={338} distance={54}>
              <div
                style={{
                  borderRadius: 34,
                  padding: "50px 46px",
                  background:
                    "linear-gradient(135deg, rgba(19,24,38,0.86), rgba(124,92,255,0.12))",
                  border: "1px solid rgba(167,139,255,0.42)",
                  boxShadow: "0 28px 120px rgba(0,0,0,0.34)",
                }}
              >
                <div
                  style={{
                    color: ACCENT,
                    fontFamily: FONT_MONO,
                    fontSize: 30,
                    fontWeight: 800,
                    marginBottom: 24,
                  }}
                >
                  YOKO TAKE
                </div>
                <div
                  style={{
                    color: INK,
                    fontSize: 68,
                    fontWeight: 900,
                    lineHeight: 1.2,
                  }}
                >
                  真正的信号：
                  <br />
                  Opus 在从“会写代码”
                  <br />
                  变成“能扛项目”。
                </div>
                <div
                  style={{
                    color: DIM,
                    fontSize: 36,
                    lineHeight: 1.42,
                    marginTop: 36,
                  }}
                >
                  如果你用 Claude Code 做迁移、排错、长链路代理，4.8 值得第一时间实测。
                </div>
              </div>
            </FadeUp>
          </div>
        )}

        <div
          style={{
            position: "absolute",
            left: 72,
            bottom: 108,
            right: 72,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            color: MUTE,
            fontFamily: FONT_MONO,
            fontSize: 24,
          }}
        >
          <span>{sources}</span>
          <span>AI 动态速报</span>
        </div>
        <Progress />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
