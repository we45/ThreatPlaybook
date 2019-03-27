<template>
    <div>
        <loading :active.sync="isLoading" :can-cancel="true" :is-full-page="isLoading"></loading>
        <nav-bar></nav-bar>
        <br>
        <b-container fluid>
            <h4>Project : {{ projectActual }}</h4>
            <hr>
            <br>
            <b-card no-body>
                <b-tabs pills card>
                    <b-tab title="Feature/User Stories" active>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <b-tree-view
                                                :data="featureData"
                                                :showIcons="true"
                                                iconClassProp="icon"
                                                prependIconClass="fas"
                                                :contextMenu="true"
                                                :contextMenuItems="contextMenuItems"
                                                @nodeSelect="nodeSelect"
                                            ></b-tree-view>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-8" v-if="selectedNode">
                                <b-card :title="nodeSelectObject.title">
                                    <b-card-text v-for="(value, key) in nodeSelectObject.data">
                                        {{ key }}: {{ value }}
                                    </b-card-text>
                                    <div v-for="(value,key) in nodeSelectObject.objs">
                                        <h3>{{ key }}</h3>
                                        <b-card-text v-for="(svalue, skey) in value">
                                            {{ skey    }}: {{ svalue }}
                                        </b-card-text>
                                    </div>
                                </b-card>
                            </div>
                        </div>
                    </b-tab>
                    <b-tab title="Scans" @click="getAllScans">
                        <br>
                        <template v-for="tgt in allScans">
                        <template v-for="scan in tgt.scans">
                            <b-list-group>
                                <b-list-group-item>
                                    <a @click="individualScan(scan.name)" style="cursor: pointer;">
                                        {{ scan.name }}
                                    </a>
                                    <!--<span style="float: right;">-->
                                    <!--<b-badge variant="success" v-if="scan.synced">synced</b-badge>-->
                                    <!--<font-awesome-icon icon="sync" v-else/>-->
                                    <!--</span>-->

                                    <span style="float: right;">
                                        {{ scan.createdOn | timeFilter}}
                                    </span>
                                    <span style="float: right;margin-right: 2%;">{{ tgt.name }}</span>
                                </b-list-group-item>
                            </b-list-group>
                            <br>
                        </template>
                        </template>
                    </b-tab>
                </b-tabs>
            </b-card>
        </b-container>
    </div>
</template>
<script>
import Navbar from "./Navbar.vue";
import gql from "graphql-tag";
import { print } from "graphql";
import Loading from "vue-loading-overlay";
import "vue-loading-overlay/dist/vue-loading.css";
import axios from "../utils/auth";
import moment from "moment";
import { bTreeView } from "bootstrap-vue-treeview";
import BCardText from "bootstrap-vue/src/components/card/card-text";

export default {
  props: ["projectName"],
  components: {
      BCardText,
    "nav-bar": Navbar,
    Loading
  },
  data() {
    return {
      isLoading: false,
      featureData: [],
      allScans: "",
      contextMenuItems: [
        { code: "DELETE_NODE", label: "Delete node" },
        {
          code: "ADD_CHILD_NODE",
          label: "Add child"
        },
        { code: "RENAME_NODE", label: "Rename" }
      ],
      selectedNode: "",
      nodeSelectObject: {}
    };
  },
  watch: {
    nodeSelectObject: function(val) {
      console.log("watch");
      this.nodeSelectObject = val;
    }
  },
  created() {
    this.projectActual = atob(this.$route.params.projectName);
    this.projectName = this.$route.params.projectName;
    this.fetchData();
    console.log("Final FeatureData " + this.featureData);
  },
  methods: {
    goToProjectMap() {
      this.$router.push("/map/" + this.projectName);
    },

    fetchData() {
      if (this.projectActual) {
        this.isLoading = true;
        const project = `"${this.projectActual}"`;
        axios
          .post("/graph", {
            query:
              "{\n" +
              "userStoryByProject(project:" +
              project +
              "){\n" +
              "id \n" +
              "shortName \n" +
              "abuses{ \n" +
              "id \n" +
              "shortName \n" +
              "models{ \n" +
              "id \n" +
              "name \n" +
              "tests{ \n" +
              "id \n" +
              "name \n" +
              "} \n" +
              "} \n" +
              "} \n" +
              "}\n" +
              "}"
          })
          .then(res => {
            this.isLoading = false;
            let responseData = res.data.data.userStoryByProject;
            for (var single in responseData) {
              var singleData = {
                id: "us:" + responseData[single].id,
                name: responseData[single].shortName,
                icon: "fa-cubes"
              };
              if (responseData[single].abuses.length > 0) {
                singleData.children = [];
                for (var abuserStory in responseData[single].abuses) {
                  var singleAbuse = {
                    id: "as:" + responseData[single].abuses[abuserStory].id,
                    name: responseData[single].abuses[abuserStory].shortName,
                    icon: "fa-warning"
                  };
                  if (
                    responseData[single].abuses[abuserStory].models.length > 0
                  ) {
                    singleAbuse.children = [];
                    for (var singleModel in responseData[single].abuses[
                      abuserStory
                    ].models) {
                      var sModel = {
                        id:
                          "mod:" +
                          responseData[single].abuses[abuserStory].models[
                            singleModel
                          ].id,
                        name:
                          responseData[single].abuses[abuserStory].models[
                            singleModel
                          ].name,
                        icon: "fa-bug"
                      };
                      if (
                        responseData[single].abuses[abuserStory].models[
                          singleModel
                        ].tests.length > 0
                      ) {
                        sModel.children = [];
                        var allTests =
                          responseData[single].abuses[abuserStory].models[
                            singleModel
                          ].tests;
                        for (var singleTest in allTests) {
                          var sTest = {
                            id: "test" + allTests[singleTest].id,
                            name: allTests[singleTest].name,
                            icon: "fa fa-check-circle"
                          };
                          sModel.children.push(sTest);
                        }
                      }
                      singleAbuse.children.push(sModel);
                    }
                  }
                  singleData.children.push(singleAbuse);
                }
              }
              this.featureData.push(singleData);
            }
          })
          .catch(error => {
            this.isLoading = false;
          });
      }
    },

    getAllScans() {
      this.isLoading = true;
      const project = `"${this.projectActual}"`;
      axios
        .post("/graph", {
          query:
            "{\n" +
            "tgtByProject(project:" +
            project +
            "){\n" +
            "name \n" +
            "scans{\n" +
            "name\n" +
            "createdOn\n" +
            "synced \n" +
            "}\n" +
            "}" +
            "}"
        })
        .then(res => {
          this.isLoading = false;
          this.allScans = res.data.data.tgtByProject;
        })
        .catch(error => {
          this.isLoading = false;
          console.log("Error", error);
        });
    },

    individualScan(scanName) {
      const scan_name = btoa(scanName);
      this.$router.push("/scan/" + scan_name);
    },

    async nodeSelect(node, isSelected) {
      await console.log(
        "Selected node " +
          node.data.name +
          " has been " +
          (isSelected ? "selected" : "deselected")
      );
      if (isSelected) {
        this.selectedNode = node.data;
        console.log(this.selectedNode.name);
        if (String(this.selectedNode.id).startsWith("us:")) {
          const usName = gql`
            query userStoryByName($shortName: String!) {
              userStoryByName(shortName: $shortName) {
                description
              }
            }
          `;

          await axios
            .post("/graph", {
              query: print(usName),
              variables: {
                shortName: this.selectedNode.name
              }
            })
            .then(res => {
              this.nodeSelectObject.data = {};
              this.nodeSelectObject.data.description =
                res.data.data.userStoryByName.description;
              this.nodeSelectObject.title = "User Story";
              console.log("graphql query done");
              console.log(this.selectedNode);
              console.log(this.nodeSelectObject);
            });
        } else if (String(this.selectedNode.id).startsWith("as:")) {
          const asName = gql`
            query abuserStoryByName($asShortName: String!) {
              abuserStoryByName(shortName: $asShortName) {
                description
              }
            }
          `;
          await axios
            .post("/graph", {
              query: print(asName),
              variables: {
                asShortName: this.selectedNode.name
              }
            })
            .then(res => {
              this.nodeSelectObject.data = {};
              this.nodeSelectObject.data.description =
                res.data.data.abuserStoryByName.description;
              this.nodeSelectObject.title = "Abuser Story";
            });
        } else if (String(this.selectedNode.id).startsWith("mod:")) {
          const modName = gql`
            query searchThreatScenario($modelName: String!) {
              searchThreatScenario(name: $modelName) {
                name
                description
                vulName
                cwe
                mitigations
                tests {
                  name
                }
              }
            }
          `;
          axios
            .post("/graph", {
              query: print(modName),
              variables: {
                modelName: this.selectedNode.name
              }
            })
            .then(res => {
              this.nodeSelectObject.data = {};
              this.nodeSelectObject.objs = {};
              let mitObj = [];
              let testObj = [];
              if (res.data.data.searchThreatScenario[0].mitigations) {
                this.nodeSelectObject.data.mitigations = [];
                for (let single in res.data.data.searchThreatScenario[0]
                  .mitigations) {
                  let mit = JSON.parse(
                    res.data.data.searchThreatScenario[0].mitigations[single]
                  );
                  console.log(typeof mit);
                  mitObj.push(mit);
                }
              }
              delete res.data.data.searchThreatScenario[0].mitigations;
              let dataObj = res.data.data.searchThreatScenario[0];
              if (dataObj.tests) {
                testObj = dataObj.tests;
                this.nodeSelectObject.objs.tests = testObj;
                delete dataObj.tests;
              }
              this.nodeSelectObject.data = dataObj;
              this.nodeSelectObject.objs.mitigations = mitObj;
              this.nodeSelectObject.title = "Threat Model";
              console.log(this.nodeSelectObject);
            });
        }
      }
      // else {
      //     this.nodeSelectObject = {}
      // }
    }
  },
  filters: {
    timeFilter: function(value) {
      if (!value) return "";
      value = moment(String(value)).format("DD-MMM-YYYY hh:mm");
      return value;
    }
  }
};
</script>

<style>
.label-high {
  width: 60px;
  border-radius: 0;
  text-shadow: none;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 5px 3px;
  text-align: center;
  color: #ffffff;
  background-color: #d11d55 !important;
}

.label-medium {
  width: 60px;
  border-radius: 0;
  text-shadow: none;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 5px 3px;
  text-align: center;
  color: #ffffff;
  background-color: #ff9c2c !important;
}

.label-low {
  width: 60px;
  border-radius: 0;
  text-shadow: none;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 5px 3px;
  text-align: center;
  color: #ffffff;
  background-color: #008b8f !important;
}

.streamline .sl-primary {
  border-left-color: #188ae2;
}

.streamline .sl-item {
  position: relative;
  padding-bottom: 12px;
  border-left: 1px solid #ccc;
}

.streamline .sl-item .text-muted {
  color: inherit;
  opacity: 0.6;
}

.streamline .sl-item p {
  margin-bottom: 10px;
}

.streamline .sl-primary {
  border-left-color: #ff4a43;
}

.streamline .sl-danger {
  border-left-color: #22beef;
}

.streamline .sl-success {
  border-left-color: #a2d200;
}

.streamline .sl-warning {
  border-left-color: #8e44ad;
}

.streamline .sl-item:before {
  content: "";
  position: absolute;
  left: -6px;
  top: 0;
  background-color: #ccc;
  width: 12px;
  height: 12px;
  border-radius: 100%;
}

.streamline .sl-primary:before,
.streamline .sl-primary:last-child:after {
  background-color: #ff4a43;
}

.streamline .sl-danger:before,
.streamline .sl-danger:last-child:after {
  background-color: #22beef;
}

.streamline .sl-success:before,
.streamline .sl-success:last-child:after {
  background-color: #a2d200;
}

.streamline .sl-warning:before,
.streamline .sl-warning:last-child:after {
  background-color: #8e44ad;
}

.card .card-body.card-padding {
  padding: 23 px 27 px;
}

.streamline .sl-item .sl-content {
  margin-left: 24px;
}

.panel-body .list-group {
  margin-bottom: 0;
}
</style>
