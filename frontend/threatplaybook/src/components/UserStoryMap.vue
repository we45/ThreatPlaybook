<template>
  <div>
    <Navbar></Navbar>
    <h5 class="text-center">User Story Map of <b>{{ projectActual }}</b></h5>
      <b-row>

        <b-col cols="12">
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
    <div v-if="nodeCaption" class="report">
      <div class="tile">
        <div class="tile is-parent is-vertical">
          <article class="tile is-child notification is-primary">
            <p style="word-wrap: break-word;overflow-wrap: break-word;hyphens: auto;text-align: center;">
              <strong>{{ nodeLabel }} : </strong>
              {{ nodeCaption }}</p>
          </article>
        </div>
      </div>
    </div>
          </b-col>
        </b-row>
  </div>
</template>
<script>
  import Navbar from "./Navbar.vue";
  import gql from "graphql-tag";
  import { Network } from "vue2vis";
  import "vue2vis/dist/vue2vis.css";
  const uuidv1 = require('uuid/v1');

export default {
    name: 'UserStoryMap',
  props: ["projectName"],
  components: {
    Navbar,
    Network
  },
  data() {
    return {
      projectActual: atob(this.projectName),
      network: {
        nodes: [],
        edges: [],
        options: {
          autoResize: true,
        width: '100%',
        height: '100%',
          nodes: {
            shape: "box",
            // size: 15,
            widthConstraint: {minimum: 150, maximum: 176,},
            widthConstraint: {minimum: 150, maximum: 176,},
            heightConstraint: { valign: 'middle' }
          },
          layout: {
            improvedLayout:false,
            hierarchical: {
              // direction: "UD",
              direction: "LR",
              sortMethod: "directed",
              // sortMethod: "hubsize",
              // levelSeparation: 150,
            }
          },
          edges: {
            smooth: {
              forceDirection: "UD"
            }
          },
          physics: {
            enabled: true
          },

        }
      },
      nodeCaption: "",
      nodeLabel: ""
    };
  },

  methods: {
    setClickEvent: function() {
      this.$refs.network.$on("click", e => {
        // console.log("Selected Node ID : " + e.nodes.toString());
        this.getSelectedNodeObject(e.nodes.toString());
      });
    },
    getSelectedNodeObject: function(inNodeID) {
      for (let i = 0; i < Object.keys(this.network.nodes).length; i++) {
        if (this.network.nodes[i].id == inNodeID) {
          console.log("label", this.network.nodes[i].label)
          console.log("title", this.network.nodes[i].title)
          this.nodeLabel = this.network.nodes[i].label
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
              relations{
                dataFlow
                endpoint
                nature
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
        // let featureRandom = Math.floor(Math.random() * 100000);
        let featureRandom = uuidv1()
        this.network.nodes.push({
          id: featureRandom,
          label: singleFeature.shortName,
          title: singleFeature.description,
          color: {
            background: "#3399ff"
          }
        });
        // let edgeFeatureRandom = Math.floor(Math.random() * 100000);
        let edgeFeatureRandom = uuidv1()
        this.network.edges.push({
          id: edgeFeatureRandom,
          from: 1,
          to: featureRandom,
          color: {
            highlight: "#3399ff"
          }
        });
        for (let singleAbuse of singleFeature.relations) {
          // let abuseRandom = Math.floor(Math.random() * 100000);
          let abuseRandom = uuidv1()
          this.network.nodes.push({
            id: abuseRandom,
            label: singleAbuse.endpoint,
            title: singleAbuse.dataFlow,
            color: {
              background: "#ffb99d"
            }
          });
          // let edgeAbuseRandom = Math.floor(Math.random() * 100000);
          let edgeAbuseRandom = uuidv1()
          this.network.edges.push({
            id: edgeAbuseRandom,
            from: featureRandom,
            to: abuseRandom,
            color: {
              highlight: "#ffb99d"
            }
          });

          // for (let singleScenario of singleAbuse.models) {
          //   let sceneRandom = Math.floor(Math.random() * 1000);
          //   this.network.nodes.push({
          //     id: sceneRandom,
          //     label: singleScenario.name,
          //     title: singleScenario.description,
          //     color: {
          //       background: "#FF6122"
          //     }
          //   });
          //   let sceneEdgeRandom = Math.floor(Math.random() * 100000);
          //   this.network.edges.push({
          //     id: sceneEdgeRandom,
          //     from: abuseRandom,
          //     to: sceneRandom,
          //     color: {
          //       highlight: "#FF6122"
          //     }
          //   });

            // for (let singleTest of singleScenario.tests) {
            //   let testRandom = Math.floor(Math.random() * 100000);
            //   this.network.nodes.push({
            //     id: testRandom,
            //     label: singleTest.name,
            //     title: singleTest.testCase,
            //     color: {
            //       background: "#16fd1a"
            //     }
            //
            //   });
            //   let testEdgeRandom = Math.floor(Math.random() * 100000);
            //   this.network.edges.push({
            //     id: testEdgeRandom,
            //     from: sceneRandom,
            //     to: testRandom,
            //     color: {
            //       highlight: "#16fd1a"
            //     }
            //   });
            }
          }
        }
      },
  created() {
    this.fetchGraphData();
    // this.projectName = this.$router.params.projectName
    // this.projectActualName = atob(this.projectName)
  }
};
</script>
<style>
.network {
  height: 500px;
  border: 1px solid #ccc;
  margin: 2%;
}

/*.network {*/
  /*display:inline-block;*/
  /*!*width:1200px;*!*/
  /*height:500px;*/
  /*border:solid;*/
  /*background-color:white;*/
/*}*/

  .report {
  display:inline-block;
  /*width:200px;*/
  /*vertical-align:top;*/
    margin-left: 5%;
    margin-right: 5%;
    text-align: center;
}

</style>
