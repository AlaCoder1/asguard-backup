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
  .addEntry("ids-ips", "./src/middleware/ids-ips.js")
  .addEntry("ipsec", "./src/middleware/ipsec.js")
  .addEntry("subscription", "./src/middleware/subscription.js")
  .addEntry("clamaV", "./src/middleware/clamaV.js")
  .addEntry("squid", "./src/middleware/squid.js")
  .addEntry("sdwan", "./src/middleware/sdwan.js")
  .addEntry("waf", "./src/middleware/waf.js")
  .addEntry("nat", "./src/middleware/nat.js")
  .addEntry("routing", "./src/middleware/routing.js")
  .addEntry("keyPair", "./src/middleware/keyPair.js")
  .addEntry("UserAndCertificateManagement", "./src/middleware/userManagment.js")
  .addEntry("404", "./src/middleware/404.js")
  .addEntry("success", "./src/middleware/success.js")
  .addEntry("vpnmonitoring", "./src/middleware/vpnmonitoring.js")
  .addEntry("interfacesType", "./src/middleware/interfaces_type.js")
  .addEntry("dhcp4-server", "./src/middleware/dhcp4-server.js")
  .addEntry("profile", "./src/middleware/profile.js")
  .addEntry("settings", "./src/middleware/settings.js")
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

  .addRule({
    test: /\.(p12)$/,
    use: [
      {
        loader: 'file-loader',
        options: {
          name: '[name].[ext]',
          outputPath: 'downloads/',  // Change the output path as needed
        },
      },
    ],
    
  })


  .configureBabelPresetEnv((config) => {
    config.useBuiltIns = "usage";
    config.corejs = 3;
  })

  .configureDefinePlugin(options => {
    options.__VUE_OPTIONS_API__ = true;
    options.__VUE_PROD_DEVTOOLS__ = false;
  })

  .enableSassLoader();

module.exports = Encore.getWebpackConfig();
