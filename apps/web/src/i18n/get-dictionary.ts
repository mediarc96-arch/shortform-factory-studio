import charactersKo from "./messages/ko-KR/characters.json";
import commonKo from "./messages/ko-KR/common.json";
import deliveryKo from "./messages/ko-KR/delivery.json";
import opsKo from "./messages/ko-KR/ops.json";
import productionKo from "./messages/ko-KR/production.json";
import requestKo from "./messages/ko-KR/request.json";
import reviewKo from "./messages/ko-KR/review.json";

import charactersEn from "./messages/en-US/characters.json";
import commonEn from "./messages/en-US/common.json";
import deliveryEn from "./messages/en-US/delivery.json";
import opsEn from "./messages/en-US/ops.json";
import productionEn from "./messages/en-US/production.json";
import requestEn from "./messages/en-US/request.json";
import reviewEn from "./messages/en-US/review.json";

import charactersJa from "./messages/ja-JP/characters.json";
import commonJa from "./messages/ja-JP/common.json";
import deliveryJa from "./messages/ja-JP/delivery.json";
import opsJa from "./messages/ja-JP/ops.json";
import productionJa from "./messages/ja-JP/production.json";
import requestJa from "./messages/ja-JP/request.json";
import reviewJa from "./messages/ja-JP/review.json";

import charactersZh from "./messages/zh-CN/characters.json";
import commonZh from "./messages/zh-CN/common.json";
import deliveryZh from "./messages/zh-CN/delivery.json";
import opsZh from "./messages/zh-CN/ops.json";
import productionZh from "./messages/zh-CN/production.json";
import requestZh from "./messages/zh-CN/request.json";
import reviewZh from "./messages/zh-CN/review.json";

import charactersEs from "./messages/es-ES/characters.json";
import commonEs from "./messages/es-ES/common.json";
import deliveryEs from "./messages/es-ES/delivery.json";
import opsEs from "./messages/es-ES/ops.json";
import productionEs from "./messages/es-ES/production.json";
import requestEs from "./messages/es-ES/request.json";
import reviewEs from "./messages/es-ES/review.json";

import type { SupportedLocale } from "./locales";

const dictionaries = {
  "ko-KR": {
    common: commonKo,
    production: productionKo,
    review: reviewKo,
    request: requestKo,
    characters: charactersKo,
    delivery: deliveryKo,
    ops: opsKo
  },
  "en-US": {
    common: commonEn,
    production: productionEn,
    review: reviewEn,
    request: requestEn,
    characters: charactersEn,
    delivery: deliveryEn,
    ops: opsEn
  },
  "ja-JP": {
    common: commonJa,
    production: productionJa,
    review: reviewJa,
    request: requestJa,
    characters: charactersJa,
    delivery: deliveryJa,
    ops: opsJa
  },
  "zh-CN": {
    common: commonZh,
    production: productionZh,
    review: reviewZh,
    request: requestZh,
    characters: charactersZh,
    delivery: deliveryZh,
    ops: opsZh
  },
  "es-ES": {
    common: commonEs,
    production: productionEs,
    review: reviewEs,
    request: requestEs,
    characters: charactersEs,
    delivery: deliveryEs,
    ops: opsEs
  }
} as const;

export type Dictionary = (typeof dictionaries)["ko-KR"];

export function getDictionary(locale: SupportedLocale): Dictionary {
  return dictionaries[locale];
}
