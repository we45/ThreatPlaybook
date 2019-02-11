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
    <div>
        <p v-if="nodeCaption">{{ nodeCaption }}</p>
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
        let featureRandom = Math.floor(Math.random() * 1000);
        this.network.nodes.push({
          id: featureRandom,
          label: singleFeature.shortName,
          title: JSON.stringify(singleFeature)
        });
        let edgeFeatureRandom = Math.floor(Math.random() * 1000);
        this.network.edges.push({
          id: edgeFeatureRandom,
          from: 1,
          to: featureRandom
        });
        for (let singleAbuse of singleFeature.abuses) {
          let abuseRandom = Math.floor(Math.random() * 1000);
          this.network.nodes.push({
            id: abuseRandom,
            label: singleAbuse.shortName,
            title: singleAbuse.description
          });
          let edgeAbuseRandom = Math.floor(Math.random() * 1000);
          this.network.edges.push({
            id: edgeAbuseRandom,
            from: featureRandom,
            to: abuseRandom
          });

          for (let singleScenario of singleAbuse.models) {
            let sceneRandom = Math.floor(Math.random() * 1000);
            this.network.nodes.push({
              id: sceneRandom,
              label: singleScenario.name,
              title: singleScenario.description
            });
            let sceneEdgeRandom = Math.floor(Math.random() * 1000);
            this.network.edges.push({
              id: sceneEdgeRandom,
              from: abuseRandom,
              to: sceneRandom
            });
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
