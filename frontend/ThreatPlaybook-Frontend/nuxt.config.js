import colors from 'vuetify/es5/util/colors'

export default {
  mode: 'universal',
  /*
   ** Headers of the page
   */
  head: {
    titleTemplate: '%s - ' + process.env.npm_package_name,
    title: process.env.npm_package_name || '',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      {
        hid: 'description',
        name: 'description',
        content: process.env.npm_package_description || ''
      }
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }]
  },
  env: {
    VUE_APP_API_URL: process.env.VUE_APP_API_URL,
    VUE_APP_GRAPH_URL: process.env.VUE_APP_GRAPH_URL
  },
  /*
   ** Customize the progress-bar color
   */
  loading: { color: '#fff' },
  /*
   ** Global CSS
   */
  css: [],
  /*
   ** Plugins to load before mounting the App
   */
  plugins: [
    { src: '~plugins/vue-apexchart.js', ssr: false },
    { src: '~plugins/vue-organization-chart.js', ssr: false }
  ],
  /*
   ** Nuxt.js dev-modules
   */
  buildModules: [
    // Doc: https://github.com/nuxt-community/eslint-module
    '@nuxtjs/eslint-module',
    // Doc: https://github.com/nuxt-community/stylelint-module
    '@nuxtjs/stylelint-module',
    '@nuxtjs/vuetify'
  ],
  /*
   ** Nuxt.js modules
   */
  modules: [
    // Doc: https://axios.nuxtjs.org/usage
    '@nuxtjs/axios',
    '@nuxtjs/apollo'
  ],
  /*
   ** Axios module configuration
   ** See https://axios.nuxtjs.org/options
   */
  axios: {},
  // Give apollo module options
  apollo: {
    // //   // tokenName: 'yourApolloTokenName', // optional, default: apollo-token
    cookieAttributes: {
      //   //     /**
      //   //      * Define when the cookie will be removed. Value can be a Number
      //   //      * which will be interpreted as days from time of creation or a
      //   //      * Date instance. If omitted, the cookie becomes a session cookie.
      //   //      */
      //   //     // expires: 1, // optional, default: 7 (days)

      //   //     /**
      //   //      * Define the path where the cookie is available. Defaults to '/'
      //   //      */
      //   //     // path: '/', // optional
      //   //     /**
      //   //      * Define the domain where the cookie is available. Defaults to
      //   //      * the domain of the page where the cookie was created.
      //   //      */
      //   //     // domain: 'example.com', // optional

      //   //     /**
      //   //      * A Boolean indicating if the cookie transmission requires a
      //   //      * secure protocol (https). Defaults to false.
      //   //      */
      secure: false
    },
    includeNodeModules: true, // optional, default: false (this includes graphql-tag for node_modules folder)
    authenticationType: '', // optional, default: 'Bearer'
    //   // (Optional) Default 'apollo' definition
    // defaultOptions: {
    //   //     // See 'apollo' definition
    //   //     // For example: default query options
    //   $query: {
    //     loadingKey: 'loading',
    //     fetchPolicy: 'cache-and-network'
    //   }
    // },
    //   // optional
    //   watchLoading: '~/plugins/apollo-watch-loading-handler.js',
    //   // optional
    //   errorHandler: '~/plugins/apollo-error-handler.js',
    //   // required
    clientConfigs: {
      default: {
        //       // required
        // httpEndpoint: process.env.VUE_APP_API_URL,

        httpEndpoint: process.env.VUE_APP_GRAPH_URL,
        getAuth: () => localStorage.getItem('token')
        //       // optional
        //       // override HTTP endpoint in browser only
        // browserHttpEndpoint: '/graphql'
        //       // optional
        //       // See https://www.apollographql.com/docs/link/links/http.html#options
        // httpLinkOptions: {
        //   credentials: 'same-origin'
        // }
        //       // You can use `wss` for secure connection (recommended in production)
        //       // Use `null` to disable subscriptions
        // wsEndpoint: 'ws://localhost:4000', // optional
        //       // LocalStorage token
        // tokenName: 'apollo-token', // optional
        //       // Enable Automatic Query persisting with Apollo Engine
        //       persisting: false, // Optional
        //       // Use websockets for everything (no HTTP)
        //       // You need to pass a `wsEndpoint` for this to work
        //       websocketsOnly: false // Optional
      }
      //     // test: {
      //     //   httpEndpoint: 'http://localhost:5000',
      //     //   wsEndpoint: 'ws://localhost:5000',
      //     //   tokenName: 'apollo-token'
      //     // },
      //     // alternative: user path to config which returns exact same config options
      //     // test2: '~/plugins/my-alternative-apollo-config.js'
    }
  },
  /*
   ** vuetify module configuration
   ** https://github.com/nuxt-community/vuetify-module
   */
  vuetify: {
    customVariables: ['~/assets/variables.scss'],
    // optionsPath: './vuetify.options.js',
    defaultAssets: {
      font: {
        family: 'Roboto'
      },
      icons: 'mdi'
    },
    theme: {
      dark: false,
      themes: {
        dark: {
          primary: colors.blue.darken2,
          accent: colors.grey.darken3,
          secondary: colors.amber.darken3,
          info: colors.teal.lighten1,
          warning: colors.amber.base,
          error: colors.deepOrange.accent4,
          success: colors.green.accent3
        }
      }
    }
  },
  /*
   ** Build configuration
   */
  build: {
    vendor: ['vue-apexchart'],
    /*
     ** You can extend webpack config here
     */
    extend(config, ctx) {
      const vueLoader = config.module.rules.find(
        (rule) => rule.loader === 'vue-loader'
      )
      vueLoader.options.transformToRequire = {
        img: 'src',
        image: 'xlink:href',
        'b-img': 'src',
        'b-img-lazy': ['src', 'blank-src'],
        'b-card': 'img-src',
        'b-card-img': 'img-src',
        'b-carousel-slide': 'img-src',
        'b-embed': 'src'
      }
    }
  }
}
