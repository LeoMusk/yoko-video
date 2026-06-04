import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring, } from "remotion";
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
export const calcEditorialFrames = (p, fps = 30) => {
    const n = p.key_points?.length ?? 0;
    const buildEnd = AT_POINT_BASE + n * AT_POINT_STEP + 30;
    return buildEnd + 12 * fps;
};
const FadeIn = ({ at, children, }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const s = spring({ frame: frame - at, fps, config: { damping: 200 } });
    const opacity = interpolate(s, [0, 1], [0, 1]);
    const ty = interpolate(s, [0, 1], [24, 0]);
    return (_jsx("div", { style: { opacity, transform: `translateY(${ty}px)` }, children: children }));
};
// 分隔线从左展开（高影响力动效）
const LineReveal = ({ at, color, height, }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const s = spring({ frame: frame - at, fps, config: { damping: 200 } });
    const w = interpolate(s, [0, 1], [0, 100]);
    return _jsx("div", { style: { height, background: color, width: `${w}%` } });
};
export const EditorialShort = (props) => {
    const { title_caption, data_points, key_points } = props;
    const hasData = (data_points?.length ?? 0) > 0;
    return (_jsxs(AbsoluteFill, { style: { backgroundColor: PAPER, fontFamily: FONT_SERIF }, children: [_jsx("div", { style: {
                    position: "absolute",
                    top: -110,
                    right: 20,
                    fontSize: 460,
                    lineHeight: 1,
                    color: RED,
                    opacity: 0.08,
                    fontFamily: FONT_NUM,
                    fontWeight: 700,
                }, children: "\u201D" }), _jsxs(AbsoluteFill, { style: {
                    flexDirection: "column",
                    justifyContent: "center",
                    alignItems: "flex-start",
                    padding: "0 76px",
                }, children: [_jsx(FadeIn, { at: AT_TITLE, children: _jsx("div", { style: {
                                color: INK,
                                fontSize: 78,
                                fontWeight: 700,
                                lineHeight: 1.32,
                            }, children: title_caption }) }), _jsx("div", { style: { width: "100%", marginTop: 40, marginBottom: 40 }, children: _jsx(LineReveal, { at: AT_LINE, color: RED, height: 6 }) }), hasData && (_jsx(FadeIn, { at: AT_DATA, children: _jsx("div", { style: { display: "flex", gap: 70, flexWrap: "wrap" }, children: data_points.slice(0, 3).map((dp, i) => (_jsxs("div", { children: [_jsx("div", { style: {
                                            fontFamily: FONT_NUM,
                                            fontSize: 104,
                                            fontWeight: 700,
                                            color: RED,
                                            lineHeight: 1,
                                        }, children: dp.value }), _jsx("div", { style: { color: GREY, fontSize: 30, marginTop: 12 }, children: dp.label })] }, i))) }) })), _jsx("div", { style: {
                            marginTop: 50,
                            display: "flex",
                            flexDirection: "column",
                            gap: 30,
                            width: "100%",
                        }, children: key_points.map((kp, i) => (_jsx(FadeIn, { at: AT_POINT_BASE + i * AT_POINT_STEP, children: _jsxs("div", { style: {
                                    display: "flex",
                                    gap: 30,
                                    alignItems: "baseline",
                                    borderBottom: `1px solid ${INK}22`,
                                    paddingBottom: 26,
                                }, children: [_jsx("div", { style: {
                                            fontFamily: FONT_NUM,
                                            fontSize: 48,
                                            fontWeight: 700,
                                            color: RED,
                                            flexShrink: 0,
                                        }, children: String(i + 1).padStart(2, "0") }), _jsx("div", { style: {
                                            color: INK,
                                            fontSize: 44,
                                            fontWeight: 600,
                                            lineHeight: 1.42,
                                        }, children: kp })] }) }, i))) })] })] }));
};
