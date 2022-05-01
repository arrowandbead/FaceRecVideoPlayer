let stuff = { content :"0-Becca Kufrin-27-Prior Lake, Minnesota-Publicist$1-Arie Luyendyk Jr.-36-Scottsdale, Arizona- Real Estate Agent and Race Car Driver$2-Lauren Burnham-25-Virginia Beach, Virginia-Technology Salesperson$3-Kendall Long-26-Santa Clarita, California-Creative Director$4-Tia Booth-26-Weiner, Arkansas-Physical Therapist$5-Bekah Martinez-22-Fresno, California-Nanny$6-Seinne Fleming-27-Long Beach, California-Commercial Real Estate Agent$7-Jacqueline Trumbull-26-Morgantown, West Virginia-Research Coordinator$8-Chelsea Roy-29-South Portland, Maine-Real Estate Executive Assistant$9-Jenna Cooper-28-Upland, Indiana-Social Media Manager$10-Krystal Nielson-29-Missoula, Montana-Fitness Coach$11-Ashley Luebke-25-West Palm Beach, Florida-Real Estate Agent$12-Maquel Cooper-23-American Fork, Utah-Photographer$13-Marikh Mathias-27-Salt Lake City, Utah-Restaurant Owner$14-Brittany Taylor-30-Belton, South Carolina-Tech Recruiter$15-Caroline Lunny-26-Holliston, Massachusetts-Realtor$16-Bibiana Julian-30-Miami, Florida-Executive Assistant$17-Annaliese Puccini-32-San Mateo, California-Event Designer$18-Lauren Schleyer-31-Dallas, Texas-Social Media Manager$19-Jennifer Delaney-25-Northbrook, Illinois-Graphic Designer$20-Lauren Griffin-26-Indianapolis, Indiana-Executive Recruiter$21-Valerie Biles-26-Nashville, Tennessee-Server$22-Alison Harrington-27-Lawton, Oklahoma-Personal Stylist$23-Amber Wilkerson-29-Denver, Colorado-Business Owner$24-Brianna Amaranthus-25-Grants Pass, Oregon-Sports Reporter$25-Brittane Johnson-27-San Diego, California-Marketing Manager$26-Jessica Carroll-26-Calgary, Alberta-Television Host$27-Lauren Jarreau-33-New Roads, Louisiana-Recent Master's Graduate$28-D'Nysha Norris-30-Anderson, South Carolina-Orthopedic Nurse$29-Olivia Goethals-23-Geneseo, Illinois-Marketing Associate"}

let splitOn$ = stuff["content"].split('$')

let splitOnDash = {}
for (let i = 0; i < splitOn$.length; i++) {
    let split = splitOn$[i].split('-')
    splitOnDash[split[1]] = split
  }

const peopleInfo = splitOnDash

export default peopleInfo