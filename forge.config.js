import type { ForgeConfig } from '@electron-forge/shared-types';
import { VitePlugin } from '@electron-forge/plugin-vite';
import { MakerSquirrel, MakerZIP, MakerDeb, MakerRPM } from '@electron-forge/maker';

const config: ForgeConfig = {
  packagerConfig: {
    asar: true,
  },
  rebuildConfig: {},
  makers: [new MakerSquirrel({}), new MakerZIP({}, ['darwin']), new MakerDeb({}), new MakerRPM({})],
  plugins: [
    new VitePlugin({
      // `config` is unknown in @electron-forge/plugin-vite 7.4.x
      mainConfig: './vite.config.main.mjs',
      renderer: {
        config: './vite.config.renderer.mjs',
        entryPoints: [
          {
            html: './src/renderer/index.html',
            js: './src/renderer/src/main.ts',
            name: 'main_window',
            preload: {
              js: './src/preload.ts',
            },
          },
        ],
      },
    }),
  ],
};

export default config;
