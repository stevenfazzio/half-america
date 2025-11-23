declare module '@matejmazur/react-katex' {
  import { ComponentType, ReactNode } from 'react';

  interface KatexProps {
    children?: string;
    math?: string;
    block?: boolean;
    errorColor?: string;
    renderError?: (error: Error) => ReactNode;
    settings?: object;
    as?: keyof JSX.IntrinsicElements;
  }

  const TeX: ComponentType<KatexProps>;
  export default TeX;
}
