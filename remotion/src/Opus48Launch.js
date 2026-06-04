import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, } from "remotion";
const FONT_CN = '"Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif';
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
    { name: "SWE-bench Verified", value: "88.6", delta: "+1.0" },
    { name: "SWE-bench Pro", value: "69.2", delta: "+4.9" },
    { name: "Terminal-Bench 2.1", value: "74.6", delta: "+8.5" },
];
const sources = "Anthropic / VentureBeat / GitHub · 2026-05-28";
export const OPUS48_DURATION = 450;
const appear = (frame, at, fps) => spring({ frame: frame - at, fps, config: { damping: 190, mass: 0.8 } });
const FadeUp = ({ at, children, distance = 34 }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const s = appear(frame, at, fps);
    return (_jsx("div", { style: {
            opacity: interpolate(s, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(s, [0, 1], [distance, 0])}px)`,
        }, children: children }));
};
const Background = () => {
    const frame = useCurrentFrame();
    const gridShift = frame * 0.35;
    const pulse = Math.sin(frame / 24) * 0.5 + 0.5;
    return (_jsxs(AbsoluteFill, { style: { backgroundColor: BG }, children: [_jsx(AbsoluteFill, { style: {
                    background: "radial-gradient(circle at 50% 35%, rgba(124,92,255,0.25), transparent 44%), radial-gradient(circle at 72% 62%, rgba(0,229,255,0.12), transparent 32%)",
                    opacity: 0.95,
                } }), _jsx(AbsoluteFill, { style: {
                    backgroundImage: "linear-gradient(rgba(124,92,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(124,92,255,0.08) 1px, transparent 1px)",
                    backgroundSize: "72px 72px",
                    backgroundPosition: `0 ${gridShift}px`,
                    opacity: 0.42,
                } }), _jsx(AbsoluteFill, { style: {
                    boxShadow: "inset 0 0 260px rgba(0,0,0,0.75)",
                } }), _jsx("div", { style: {
                    position: "absolute",
                    inset: 0,
                    background: "linear-gradient(115deg, transparent 0%, rgba(255,255,255,0.06) 48%, transparent 58%)",
                    transform: `translateX(${interpolate(frame, [0, OPUS48_DURATION], [-900, 900])}px)`,
                    opacity: 0.26 + pulse * 0.1,
                } })] }));
};
const ProductSquare = () => {
    const frame = useCurrentFrame();
    const rotate = frame * 1.8;
    const glow = Math.sin(frame / 13) * 0.5 + 0.5;
    return (_jsx("div", { style: {
            position: "relative",
            width: 500,
            height: 500,
            borderRadius: 46,
            padding: 7,
            background: `conic-gradient(from ${rotate}deg, ${ACCENT}, ${CYAN}, ${PINK}, ${ACCENT})`,
            boxShadow: `0 28px 110px rgba(124,92,255,${0.24 + glow * 0.12})`,
        }, children: _jsxs("div", { style: {
                width: "100%",
                height: "100%",
                borderRadius: 39,
                background: "linear-gradient(145deg, #1A0F2E, #080812 72%)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                border: `1px solid ${LINE}`,
            }, children: [_jsx("div", { style: {
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
                        boxShadow: "0 28px 86px rgba(217,119,87,0.38), inset 0 3px 0 rgba(255,255,255,0.22)",
                    }, children: "\u2731" }), _jsx("div", { style: {
                        color: INK,
                        fontSize: 44,
                        fontWeight: 800,
                        marginTop: 38,
                    }, children: "Claude Opus" }), _jsx("div", { style: {
                        color: DIM,
                        fontFamily: FONT_MONO,
                        fontSize: 35,
                        marginTop: 10,
                    }, children: "v4.8 \u00B7 NOW LIVE" })] }) }));
};
const FactCard = ({ item, index }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const s = appear(frame, 96 + index * 8, fps);
    return (_jsxs("div", { style: {
            opacity: interpolate(s, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(s, [0, 1], [44, 0])}px)`,
            background: "rgba(19,24,38,0.78)",
            border: `1px solid ${LINE}`,
            borderRadius: 28,
            width: 304,
            height: 210,
            padding: "25px 22px",
            textAlign: "center",
        }, children: [_jsx("div", { style: {
                    color: MUTE,
                    fontSize: 27,
                    letterSpacing: 0,
                    fontWeight: 600,
                }, children: item.label }), _jsx("div", { style: {
                    color: item.color,
                    fontFamily: FONT_MONO,
                    fontSize: 66,
                    fontWeight: 900,
                    lineHeight: 1,
                    marginTop: 18,
                }, children: item.value }), _jsx("div", { style: {
                    color: DIM,
                    fontFamily: FONT_MONO,
                    fontSize: 24,
                    marginTop: 15,
                    whiteSpace: "pre-wrap",
                }, children: item.sub })] }));
};
const BenchCard = ({ item, index }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const s = appear(frame, 224 + index * 9, fps);
    return (_jsxs("div", { style: {
            opacity: interpolate(s, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(s, [0, 1], [50, 0])}px)`,
            height: 146,
            borderRadius: 26,
            background: index === 0
                ? "linear-gradient(135deg, rgba(124,92,255,0.24), rgba(124,92,255,0.06))"
                : "rgba(19,24,38,0.7)",
            border: `1px solid ${index === 0 ? "rgba(167,139,255,0.6)" : LINE}`,
            padding: "22px 30px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
        }, children: [_jsxs("div", { children: [_jsx("div", { style: { color: INK, fontSize: 35, fontWeight: 750 }, children: item.name }), _jsx("div", { style: {
                            color: MUTE,
                            fontFamily: FONT_MONO,
                            fontSize: 24,
                            marginTop: 10,
                        }, children: "vs Opus 4.7" })] }), _jsxs("div", { style: { textAlign: "right" }, children: [_jsx("div", { style: {
                            color: index === 0 ? ACCENT : INK,
                            fontFamily: FONT_MONO,
                            fontSize: 60,
                            fontWeight: 900,
                            lineHeight: 1,
                        }, children: item.value }), _jsxs("div", { style: {
                            color: UP,
                            fontFamily: FONT_MONO,
                            fontSize: 28,
                            fontWeight: 800,
                            marginTop: 8,
                        }, children: ["\u25B2 ", item.delta] })] })] }));
};
const Progress = () => {
    const frame = useCurrentFrame();
    const width = interpolate(frame, [0, OPUS48_DURATION - 1], [0, 100], {
        extrapolateRight: "clamp",
    });
    return (_jsx("div", { style: {
            position: "absolute",
            left: 72,
            bottom: 70,
            width: 936,
            height: 7,
            borderRadius: 99,
            background: "rgba(255,255,255,0.12)",
            overflow: "hidden",
        }, children: _jsx("div", { style: {
                width: `${width}%`,
                height: "100%",
                background: `linear-gradient(90deg, ${ACCENT}, ${CYAN})`,
            } }) }));
};
export const Opus48Launch = () => {
    const frame = useCurrentFrame();
    const scene2 = frame >= 88;
    const scene3 = frame >= 210;
    const final = frame >= 338;
    const titleOpacity = final ? 0.22 : 1;
    const productOpacity = scene2 ? (scene3 ? 0 : 1) : 1;
    const factsOpacity = scene2 && !scene3 ? 1 : 0;
    const benchOpacity = scene3 && !final ? 1 : 0;
    return (_jsxs(AbsoluteFill, { style: { fontFamily: FONT_CN, color: INK }, children: [_jsx(Background, {}), _jsxs(AbsoluteFill, { style: { padding: "0 72px" }, children: [_jsxs("div", { style: {
                            position: "absolute",
                            top: 116,
                            left: 72,
                            right: 72,
                            opacity: titleOpacity,
                        }, children: [_jsx(FadeUp, { at: 0, children: _jsx("div", { style: {
                                        color: MUTE,
                                        fontSize: 30,
                                        fontWeight: 650,
                                        letterSpacing: 0,
                                    }, children: "\uD83D\uDD34 \u91CD\u78C5\u53D1\u5E03 \u00B7 2026-05-28" }) }), _jsx(FadeUp, { at: 8, children: _jsxs("div", { style: {
                                        color: INK,
                                        fontSize: 86,
                                        fontWeight: 900,
                                        lineHeight: 1.08,
                                        marginTop: 24,
                                        textShadow: "0 0 42px rgba(124,92,255,0.35)",
                                    }, children: ["Claude Opus 4.8", _jsx("br", {}), "\u521A\u521A\u4E0A\u7EBF"] }) }), _jsx(FadeUp, { at: 18, children: _jsx("div", { style: {
                                        color: DIM,
                                        fontSize: 38,
                                        lineHeight: 1.3,
                                        marginTop: 22,
                                    }, children: "\u4E0D\u662F\u201C\u6362\u76AE\u66F4\u65B0\u201D\uFF0C\u800C\u662F\u628A\u5F00\u53D1\u8005\u6700\u75BC\u7684\u4EF7\u683C\u548C\u957F\u4EFB\u52A1\u7A33\u5B9A\u6027\u4E00\u8D77\u8865\u4E86\u3002" }) })] }), _jsx("div", { style: {
                            position: "absolute",
                            top: 600,
                            left: 290,
                            opacity: productOpacity,
                            transform: `scale(${scene2 ? 0.78 : 1}) translateY(${scene2 ? -38 : 0}px)`,
                        }, children: _jsx(FadeUp, { at: 28, children: _jsx(ProductSquare, {}) }) }), _jsx("div", { style: {
                            position: "absolute",
                            top: 1080,
                            left: 48,
                            right: 48,
                            display: "flex",
                            gap: 18,
                            opacity: factsOpacity,
                        }, children: facts.map((item, index) => (_jsx(FactCard, { item: item, index: index }, item.label))) }), _jsxs("div", { style: {
                            position: "absolute",
                            top: 438,
                            left: 72,
                            right: 72,
                            opacity: benchOpacity,
                        }, children: [_jsx(FadeUp, { at: 210, children: _jsxs("div", { style: {
                                        color: INK,
                                        fontSize: 58,
                                        fontWeight: 880,
                                        lineHeight: 1.12,
                                        marginBottom: 30,
                                    }, children: ["\u6027\u80FD\u4E0D\u662F\u66B4\u8DF3\uFF0C", _jsx("br", {}), "\u4F46\u5173\u952E\u699C\u5355\u90FD\u5728\u6DA8"] }) }), _jsx("div", { style: { display: "flex", flexDirection: "column", gap: 22 }, children: bench.map((item, index) => (_jsx(BenchCard, { item: item, index: index }, item.name))) }), _jsx(FadeUp, { at: 262, children: _jsx("div", { style: {
                                        color: DIM,
                                        fontSize: 34,
                                        lineHeight: 1.35,
                                        marginTop: 34,
                                    }, children: "GitHub Copilot \u4E5F\u5DF2\u7ECF\u63A5\u5165\uFF0C\u4F46\u4F01\u4E1A/\u5546\u4E1A\u7528\u6237\u9700\u8981\u7BA1\u7406\u5458\u5F00\u542F\u7B56\u7565\u3002" }) })] }), final && (_jsx("div", { style: {
                            position: "absolute",
                            top: 506,
                            left: 72,
                            right: 72,
                        }, children: _jsx(FadeUp, { at: 338, distance: 54, children: _jsxs("div", { style: {
                                    borderRadius: 34,
                                    padding: "50px 46px",
                                    background: "linear-gradient(135deg, rgba(19,24,38,0.86), rgba(124,92,255,0.12))",
                                    border: "1px solid rgba(167,139,255,0.42)",
                                    boxShadow: "0 28px 120px rgba(0,0,0,0.34)",
                                }, children: [_jsx("div", { style: {
                                            color: ACCENT,
                                            fontFamily: FONT_MONO,
                                            fontSize: 30,
                                            fontWeight: 800,
                                            marginBottom: 24,
                                        }, children: "YOKO TAKE" }), _jsxs("div", { style: {
                                            color: INK,
                                            fontSize: 68,
                                            fontWeight: 900,
                                            lineHeight: 1.2,
                                        }, children: ["\u771F\u6B63\u7684\u4FE1\u53F7\uFF1A", _jsx("br", {}), "Opus \u5728\u4ECE\u201C\u4F1A\u5199\u4EE3\u7801\u201D", _jsx("br", {}), "\u53D8\u6210\u201C\u80FD\u625B\u9879\u76EE\u201D\u3002"] }), _jsx("div", { style: {
                                            color: DIM,
                                            fontSize: 36,
                                            lineHeight: 1.42,
                                            marginTop: 36,
                                        }, children: "\u5982\u679C\u4F60\u7528 Claude Code \u505A\u8FC1\u79FB\u3001\u6392\u9519\u3001\u957F\u94FE\u8DEF\u4EE3\u7406\uFF0C4.8 \u503C\u5F97\u7B2C\u4E00\u65F6\u95F4\u5B9E\u6D4B\u3002" })] }) }) })), _jsxs("div", { style: {
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
                        }, children: [_jsx("span", { children: sources }), _jsx("span", { children: "AI \u52A8\u6001\u901F\u62A5" })] }), _jsx(Progress, {})] })] }));
};
