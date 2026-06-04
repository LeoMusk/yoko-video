import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { Composition } from "remotion";
import { YokoShort, calcDurationInFrames } from "./YokoShort";
import { EditorialShort, calcEditorialFrames } from "./EditorialShort";
import { Opus48Launch, OPUS48_DURATION } from "./Opus48Launch";
import propsData from "../props.json";
const FPS = 30;
const SIZE = { fps: FPS, width: 1080, height: 1920 };
export const RemotionRoot = () => {
    const data = propsData;
    return (_jsxs(_Fragment, { children: [_jsx(Composition, { id: "YokoShort", component: YokoShort, durationInFrames: calcDurationInFrames(data), defaultProps: data, ...SIZE }), _jsx(Composition, { id: "EditorialShort", component: EditorialShort, durationInFrames: calcEditorialFrames(data), defaultProps: data, ...SIZE }), _jsx(Composition, { id: "Opus48Launch", component: Opus48Launch, durationInFrames: OPUS48_DURATION, defaultProps: {}, ...SIZE })] }));
};
