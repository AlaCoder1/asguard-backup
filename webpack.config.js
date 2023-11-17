const path = require("path");
const Encore = require("@symfony/webpack-encore");

// const VuetifyLoaderPlugin = require('vuetify-loader/lib/plugin');
// .addPlugin(new VuetifyLoaderPlugin())

if (!Encore.isRuntimeEnvironmentConfigured()) {
  Encore.configureRuntimeEnvironment(process.env.NODE_ENV || "dev");
}
Encore.setOutputPath("static/")

  .setPublicPath("/static")
  .setManifestKeyPrefix("static/")
  .addEntry("app", "./src/middleware/app.js")
  .addEntry("home", "./src/middleware/home.js")
  .addEntry("login", "./src/middleware/login.js")
  .addEntry("ifName", "./src/middleware/ifName.js")
  .addEntry("firewall", "./src/middleware/firewall.js")
  .addEntry("openvpn", "./src/middleware/openvpn.js")
  // .addEntry("settings", "./src/middleware/settings.js")
  .addEntry("ipsec", "./src/middleware/ipsec.js")
  .addEntry("UserAndCertificateManagement", "./src/middleware/userManagment.js")
  .addEntry("404", "./src/middleware/404.js")
  .enableVueLoader(() => {}, {
    version: 3,
  })

  .addAliases({
    "@": path.resolve(__dirname, "./src"),
  })

  .splitEntryChunks()
  .enableSingleRuntimeChunk()
  .cleanupOutputBeforeBuild()
  .enableBuildNotifications()
  .enableSourceMaps(!Encore.isProduction())
  .enableVersioning(Encore.isProduction())

  .configureBabel((config) => {
    config.plugins.push("@babel/plugin-proposal-class-properties");
  })

  .configureBabelPresetEnv((config) => {
    config.useBuiltIns = "usage";
    config.corejs = 3;
  })
  .enableSassLoader();

module.exports = Encore.getWebpackConfig();
