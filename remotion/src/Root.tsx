import React from "react";
import {Composition} from "remotion";
import {YokoShort, calcDurationInFrames, YokoShortProps} from "./YokoShort";
import {EditorialShort, calcEditorialFrames} from "./EditorialShort";
import {Opus48Launch, OPUS48_DURATION} from "./Opus48Launch";
import {BreakingFlash, BREAKING_FLASH_DURATION, BreakingFlashProps} from "./BreakingFlash";
import propsData from "../props.json";
import breakingFlashData from "../breaking-flash.json";

const FPS = 30;
const SIZE = {fps: FPS, width: 1080, height: 1920} as const;

export const RemotionRoot: React.FC = () => {
  const data = propsData as unknown as YokoShortProps;
  return (
    <>
      <Composition
        id="YokoShort"
        component={YokoShort}
        durationInFrames={calcDurationInFrames(data)}
        defaultProps={data}
        {...SIZE}
      />
      <Composition
        id="EditorialShort"
        component={EditorialShort}
        durationInFrames={calcEditorialFrames(data)}
        defaultProps={data}
        {...SIZE}
      />
      <Composition
        id="Opus48Launch"
        component={Opus48Launch}
        durationInFrames={OPUS48_DURATION}
        defaultProps={{}}
        {...SIZE}
      />
      <Composition
        id="BreakingFlash"
        component={BreakingFlash}
        durationInFrames={BREAKING_FLASH_DURATION}
        defaultProps={breakingFlashData as unknown as BreakingFlashProps}
        {...SIZE}
      />
    </>
  );
};
