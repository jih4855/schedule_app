import { defineConfig } from '@apps-in-toss/web-framework/config';

export default defineConfig({
  appName: 'llm-scheduler',
  brand: {
    displayName: 'AI 일정관리', // 화면에 노출될 앱의 한글 이름으로 바꿔주세요.
    primaryColor: '#6c63ff', // 화면에 노출될 앱의 기본 색상으로 바꿔주세요.
    icon:"", // 화면에 노출될 앱의 아이콘 이미지 주소로 바꿔주세요.
    bridgeColorMode: 'basic',
  },
  web: {
    host: 'localhost',
    port: 3000,
    commands: {
      dev: 'npm start',
      build: 'npm run build',
    },
  },
  permissions: [],
  outdir: 'build',
});
