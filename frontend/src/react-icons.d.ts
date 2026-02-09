/**
 * react-icons の型互換性修正
 *
 * 変更理由: React 19の型定義とreact-icons 5.xの型定義に
 * 互換性問題があるため、モジュール宣言でオーバーライド。
 */
declare module 'react-icons/lu' {
  import { ComponentType, SVGAttributes } from 'react';

  interface IconProps extends SVGAttributes<SVGElement> {
    size?: string | number;
    color?: string;
    title?: string;
    className?: string;
  }

  type IconType = ComponentType<IconProps>;

  export const LuLayoutDashboard: IconType;
  export const LuListChecks: IconType;
  export const LuLightbulb: IconType;
  export const LuBookOpen: IconType;
  export const LuSparkles: IconType;
  export const LuLogOut: IconType;
  export const LuMenu: IconType;
  export const LuX: IconType;
  export const LuZap: IconType;
  export const LuRefreshCw: IconType;
  export const LuDatabase: IconType;
  export const LuCheck: IconType;
  export const LuLoader: IconType;
  export const LuCircleCheck: IconType;
  export const LuFolder: IconType;
  export const LuFolderKanban: IconType;
  export const LuPlus: IconType;
  export const LuTrash2: IconType;
  export const LuGithub: IconType;
  export const LuClipboardList: IconType;
  export const LuArrowRight: IconType;
  export const LuTag: IconType;
  export const LuHardHat: IconType;
}

declare module 'react-icons' {
  import { ComponentType, SVGAttributes } from 'react';

  export interface IconBaseProps extends SVGAttributes<SVGElement> {
    size?: string | number;
    color?: string;
    title?: string;
  }

  export type IconType = ComponentType<IconBaseProps>;
}
