<template>
  <div>
    <div>
      <network
        class="network"
        ref="network"
        :nodes="network.nodes"
        :edges="network.edges"
        :options="network.options"
        @select-node="setClickEvent()"
      ></network>
    </div>
    <div v-if="nodeCaption">
      <div class="tile">
        <div class="tile is-parent is-vertical">
          <article class="tile is-child notification is-primary">
            <p>{{ nodeCaption }}</p>
          </article>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import gql from "graphql-tag";
import { Network } from "vue2vis";
export default {
  props: ["projectName"],
  data() {
    return {
      projectActual: atob(this.projectName),
      network: {
        nodes: [],
        edges: [],
        options: {
          nodes: {
            shape: "dot"
          },
          layout: {
            hierarchical: {
              direction: "UD",
              sortMethod: "directed"
            }
          },
          edges: {
            smooth: {
              forceDirection: "UD"
            }
          },
          physics: {
            enabled: false
          }
        }
      },
      nodeCaption: ""
    };
  },
  components: {
    Network
  },
  methods: {
    setClickEvent: function() {
      this.$refs.network.$on("click", e => {
        console.log("Selected Node ID : " + e.nodes.toString());
        console.log(this.getSelectedNodeObject(e.nodes.toString()));
      });
    },
    getSelectedNodeObject: function(inNodeID) {
      for (let i = 0; i < Object.keys(this.network.nodes).length; i++) {
        if (this.network.nodes[i].id == inNodeID) {
          this.nodeCaption = this.network.nodes[i].title;
        }
      }
      return null;
    },
    async fetchGraphData() {
      const result = await this.$apollo.query({
        query: gql`
          query singleProjectQuery($pname: String!) {
            userStoryByProject(project: $pname) {
              shortName
              description
              abuses {
                shortName
                description
                models {
                  name
                  description
                  cwe
                  severity
                  tests {
                    name
                    testCase
                    testType
                  }
                }
              }
            }
          }
        `,
        variables: {
          pname: this.projectActual
        }
      });
      //Code to push data into the nodes
      this.network.nodes.push({
        id: 1,
        label: `Project: ${this.projectActual}`
      });
      for (let singleFeature of result.data.userStoryByProject) {
        let featureRandom = Math.floor(Math.random() * 100000);
        this.network.nodes.push({
          id: featureRandom,
          label: singleFeature.shortName,
          title: singleFeature.description,
          color: {
            background: "#3399ff"
          }
        });
        let edgeFeatureRandom = Math.floor(Math.random() * 100000);
        this.network.edges.push({
          id: edgeFeatureRandom,
          from: 1,
          to: featureRandom,
          color: {
            highlight: "#3399ff"
          }
        });
        for (let singleAbuse of singleFeature.abuses) {
          let abuseRandom = Math.floor(Math.random() * 100000);
          this.network.nodes.push({
            id: abuseRandom,
            label: singleAbuse.shortName,
            title: singleAbuse.description,
            color: {
              background: "#ffb99d"
            }
          });
          let edgeAbuseRandom = Math.floor(Math.random() * 100000);
          this.network.edges.push({
            id: edgeAbuseRandom,
            from: featureRandom,
            to: abuseRandom,
            color: {
              highlight: "#ffb99d"
            }
          });

          for (let singleScenario of singleAbuse.models) {
            let sceneRandom = Math.floor(Math.random() * 1000);
            this.network.nodes.push({
              id: sceneRandom,
              label: singleScenario.name,
              title: singleScenario.description,
              color: {
                background: "#FF6122"
              }
            });
            let sceneEdgeRandom = Math.floor(Math.random() * 100000);
            this.network.edges.push({
              id: sceneEdgeRandom,
              from: abuseRandom,
              to: sceneRandom,
              color: {
                highlight: "#FF6122"
              }
            });

            for (let singleTest of singleScenario.tests) {
              let testRandom = Math.floor(Math.random() * 100000);
              this.network.nodes.push({
                id: testRandom,
                label: singleTest.name,
                title: singleTest.testCase,
                color: {
                  background: "#16fd1a"
                }
              });
              let testEdgeRandom = Math.floor(Math.random() * 100000);
              this.network.edges.push({
                id: testEdgeRandom,
                from: sceneRandom,
                to: testRandom,
                color: {
                  highlight: "#16fd1a"
                }
              });
            }
          }
        }
      }
    }
  },
  created() {
    this.fetchGraphData();
  }
};
</script>
<style>
.network {
  height: 600px;
  border: 1px solid #ccc;
  margin: 5px 0;
}
</style>
