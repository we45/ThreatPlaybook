module.exports = {
  title: "Threat Playbook",
  tagline:
    "A (relatively) Unopinionated framework that faciliates Threat Modeling as Code married with Application Security Automation on a single Fabric",
  url: "https://your-docusaurus-test-site.com",
  baseUrl: "/",
  favicon: "img/favicon.ico",
  organizationName: "we45",
  projectName: "ThreatPlaybook",
  themeConfig: {
    navbar: {
      logo: {
        alt: "Logo",
        src: "img/logo.png",
      },
      links: [
        {
          to: "docs",
          activeBasePath: "/",
          label: "Documentation",
          position: "left",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Community",
          items: [
            {
              label: "Twitter",
              href: "https://twitter.com/we45",
            },
          ],
        },
        {
          title: "More",
          items: [
            {
              label: "GitHub",
              href: "https://github.com/we45/ThreatPlaybook",
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} we45, Inc. Built with Docusaurus.`,
    },
  },
  presets: [
    [
      "@docusaurus/preset-classic",
      {
        docs: {
          homePageId: "overview",
          sidebarPath: require.resolve("./sidebars.js"),
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      },
    ],
  ],
};
