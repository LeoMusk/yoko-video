import {Config} from "@remotion/cli/config";
import {existsSync} from "node:fs";

// 优先用系统已装浏览器，避免从 Google 下载 chrome-headless-shell（国内网络常受阻）。
// 可用 REMOTION_CHROME_EXECUTABLE 环境变量覆盖。
const browserCandidates = [
  process.env.REMOTION_CHROME_EXECUTABLE,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
].filter((p): p is string => Boolean(p));

const found = browserCandidates.find((p) => existsSync(p));
if (found) {
  Config.setBrowserExecutable(found);
}
